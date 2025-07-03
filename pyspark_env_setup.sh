# PySpark Environment Setup
# Add this to your shell profile (.bashrc, .zshrc, etc.)

# Java (adjust path as needed)
export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/default-java}

# PySpark
export PYSPARK_PYTHON=${PYSPARK_PYTHON:-python3}
export PYSPARK_DRIVER_PYTHON=${PYSPARK_DRIVER_PYTHON:-python3}

# Reduce Spark logging (optional)
export SPARK_LOCAL_IP=127.0.0.1

# Add to PATH
export PATH=$JAVA_HOME/bin:$PATH
