"""
Enhanced table detection for Excel sheets.
Identifies proper tabular data structures and skips informational/non-tabular content.
"""

from typing import List, Tuple, Optional, Dict, Any
import re
from collections import Counter


class TableDetector:
    """Detects tabular data structures in Excel sheets."""
    
    def __init__(self):
        self.min_data_rows = 2  # Minimum rows to consider a table
        self.min_columns = 2    # Minimum columns to consider a table
        self.max_empty_ratio = 0.7  # Maximum ratio of empty cells allowed
        
    def detect_table_structure(self, sheet, sheet_name: str) -> Dict[str, Any]:
        """
        Detect if a sheet contains a proper table structure.
        
        Returns:
            Dict containing:
            - has_table: bool
            - table_start_row: int (1-based)
            - headers: List[str]
            - data_rows: int
            - confidence: float (0-1)
            - issues: List[str]
        """
        result = {
            'has_table': False,
            'table_start_row': 1,
            'headers': [],
            'data_rows': 0,
            'confidence': 0.0,
            'issues': []
        }
        
        # Get sheet dimensions
        if hasattr(sheet, 'max_row'):
            max_row = sheet.max_row or 0
            max_col = sheet.max_column or 0
        else:
            # Read-only mode - count by iteration
            max_row = sum(1 for _ in sheet.rows)
            max_col = len(next(sheet.rows, [])) if max_row > 0 else 0
        
        if max_row < self.min_data_rows:
            result['issues'].append(f"Too few rows ({max_row}), minimum required: {self.min_data_rows}")
            return result
        
        if max_col < self.min_columns:
            result['issues'].append(f"Too few columns ({max_col}), minimum required: {self.min_columns}")
            return result
        
        # Try to find the header row and analyze table structure
        table_info = self._find_table_boundaries(sheet, max_row, max_col)
        
        if not table_info:
            result['issues'].append("No clear table structure detected")
            return result
        
        # Extract table information
        result['table_start_row'] = table_info['header_row']
        result['headers'] = table_info['headers']
        result['data_rows'] = table_info['data_rows']
        
        # Calculate confidence score
        confidence = self._calculate_confidence(table_info, max_row, max_col)
        result['confidence'] = confidence
        
        # Determine if this is a valid table
        if confidence >= 0.6 and table_info['data_rows'] >= self.min_data_rows:
            result['has_table'] = True
        else:
            if confidence < 0.6:
                result['issues'].append(f"Low confidence score: {confidence:.2f}")
            if table_info['data_rows'] < self.min_data_rows:
                result['issues'].append(f"Insufficient data rows: {table_info['data_rows']}")
        
        return result
    
    def _find_table_boundaries(self, sheet, max_row: int, max_col: int) -> Optional[Dict[str, Any]]:
        """Find the boundaries of the table within the sheet."""
        best_candidate = None
        best_score = 0
        
        # Look for potential header rows in the first 10 rows
        for potential_header_row in range(1, min(11, max_row + 1)):
            candidate = self._analyze_potential_table(sheet, potential_header_row, max_row, max_col)
            
            if candidate and candidate['score'] > best_score:
                best_score = candidate['score']
                best_candidate = candidate
        
        return best_candidate
    
    def _analyze_potential_table(self, sheet, header_row: int, max_row: int, max_col: int) -> Optional[Dict[str, Any]]:
        """Analyze a potential table starting at the given header row."""
        # Extract potential headers
        headers = []
        header_cells = []
        
        if hasattr(sheet, 'iter_rows'):
            # Standard mode
            for cell in sheet[header_row]:
                if cell.column <= max_col:
                    headers.append(str(cell.value) if cell.value else "")
                    header_cells.append(cell)
        else:
            # Read-only mode
            for row_idx, row in enumerate(sheet.rows):
                if row_idx + 1 == header_row:
                    for cell in row:
                        headers.append(str(cell.value) if cell.value else "")
                        header_cells.append(cell)
                    break
        
        if not headers:
            return None
        
        # Clean and validate headers
        clean_headers = [h.strip() for h in headers if h.strip()]
        
        if len(clean_headers) < self.min_columns:
            return None
        
        # Check header quality
        header_score = self._score_headers(clean_headers)
        
        if header_score < 0.3:  # Headers are too poor quality
            return None
        
        # Analyze data rows
        data_analysis = self._analyze_data_consistency(sheet, header_row + 1, max_row, len(headers))
        
        if not data_analysis:
            return None
        
        # Calculate overall score
        overall_score = (header_score * 0.4 + data_analysis['consistency_score'] * 0.6)
        
        return {
            'header_row': header_row,
            'headers': clean_headers,
            'data_rows': data_analysis['valid_rows'],
            'total_cells': data_analysis['total_cells'],
            'empty_cells': data_analysis['empty_cells'],
            'consistency_score': data_analysis['consistency_score'],
            'header_score': header_score,
            'score': overall_score
        }
    
    def _score_headers(self, headers: List[str]) -> float:
        """Score the quality of potential headers."""
        if not headers:
            return 0.0
        
        score = 0.0
        total_checks = 0
        
        # Check 1: Non-empty headers
        non_empty = sum(1 for h in headers if h.strip())
        score += (non_empty / len(headers)) * 0.3
        total_checks += 0.3
        
        # Check 2: Unique headers
        unique_headers = len(set(h.lower().strip() for h in headers if h.strip()))
        if non_empty > 0:
            score += (unique_headers / non_empty) * 0.3
            total_checks += 0.3
        
        # Check 3: Header-like patterns (avoid purely numeric, avoid very long text)
        header_like = 0
        for header in headers:
            h = header.strip()
            if not h:
                continue
            
            # Good header indicators
            if len(h) <= 50 and not h.isdigit() and not self._looks_like_sentence(h):
                header_like += 1
        
        if non_empty > 0:
            score += (header_like / non_empty) * 0.4
            total_checks += 0.4
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _looks_like_sentence(self, text: str) -> bool:
        """Check if text looks like a sentence rather than a column header."""
        if len(text) > 100:  # Very long text
            return True
        
        # Count spaces - headers typically have fewer spaces
        space_ratio = text.count(' ') / len(text) if text else 0
        if space_ratio > 0.3:  # More than 30% spaces
            return True
        
        # Check for sentence-ending punctuation
        if text.endswith(('.', '!', '?')):
            return True
        
        return False
    
    def _analyze_data_consistency(self, sheet, start_row: int, max_row: int, num_cols: int) -> Optional[Dict[str, Any]]:
        """Analyze consistency of data rows."""
        if start_row > max_row:
            return None
        
        total_cells = 0
        empty_cells = 0
        valid_rows = 0
        row_completeness = []
        
        # Analyze each data row
        data_rows_analyzed = 0
        
        if hasattr(sheet, 'iter_rows'):
            # Standard mode
            for row in sheet.iter_rows(min_row=start_row, max_row=max_row):
                if data_rows_analyzed >= 100:  # Limit analysis for performance
                    break
                
                row_data = [cell.value for cell in row[:num_cols]]
                non_empty_in_row = sum(1 for val in row_data if val is not None and str(val).strip())
                
                total_cells += len(row_data)
                empty_cells += len(row_data) - non_empty_in_row
                
                # Consider a row valid if it has at least some data
                if non_empty_in_row > 0:
                    valid_rows += 1
                    row_completeness.append(non_empty_in_row / len(row_data))
                
                data_rows_analyzed += 1
        else:
            # Read-only mode
            for row_idx, row in enumerate(sheet.rows):
                if row_idx + 1 < start_row:
                    continue
                if row_idx + 1 > max_row or data_rows_analyzed >= 100:
                    break
                
                row_data = [cell.value for cell in row[:num_cols]]
                non_empty_in_row = sum(1 for val in row_data if val is not None and str(val).strip())
                
                total_cells += len(row_data)
                empty_cells += len(row_data) - non_empty_in_row
                
                if non_empty_in_row > 0:
                    valid_rows += 1
                    row_completeness.append(non_empty_in_row / len(row_data))
                
                data_rows_analyzed += 1
        
        if valid_rows == 0:
            return None
        
        # Calculate consistency score
        empty_ratio = empty_cells / total_cells if total_cells > 0 else 1.0
        avg_completeness = sum(row_completeness) / len(row_completeness) if row_completeness else 0
        
        # Consistency score based on data density and row completeness
        consistency_score = (1 - empty_ratio) * 0.6 + avg_completeness * 0.4
        
        return {
            'valid_rows': valid_rows,
            'total_cells': total_cells,
            'empty_cells': empty_cells,
            'empty_ratio': empty_ratio,
            'avg_completeness': avg_completeness,
            'consistency_score': min(consistency_score, 1.0)
        }
    
    def _calculate_confidence(self, table_info: Dict[str, Any], total_rows: int, total_cols: int) -> float:
        """Calculate overall confidence in the table detection."""
        # Factors that increase confidence:
        # 1. Good header quality
        # 2. High data consistency
        # 3. Reasonable data-to-sheet ratio
        # 4. Sufficient data rows
        
        header_factor = table_info['header_score']
        consistency_factor = table_info['consistency_score']
        
        # Data coverage factor (how much of the sheet is actual table data)
        data_coverage = table_info['data_rows'] / total_rows if total_rows > 0 else 0
        coverage_factor = min(data_coverage * 2, 1.0)  # Cap at 1.0
        
        # Size factor (prefer tables with reasonable size)
        size_factor = 1.0
        if table_info['data_rows'] < 3:
            size_factor *= 0.7
        elif table_info['data_rows'] > 50:
            size_factor *= 1.1  # Bonus for larger tables
        
        # Combine factors
        confidence = (header_factor * 0.3 + 
                     consistency_factor * 0.4 + 
                     coverage_factor * 0.2 + 
                     size_factor * 0.1)
        
        return min(confidence, 1.0)