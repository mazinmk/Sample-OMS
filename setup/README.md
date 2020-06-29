# Sample Retail Order Management System
To design a sample **retail order management system** which has the capability to process a couple of millions orders per day.

# Technical stack 
* OS : Ubuntu-18.04
* Messaging: kafka_2.13-2.5.0
* Time series Database: Druid
* Analytics: Imply-3.3.5
* Metastore: MongoDB-3.6.3
* Dataprocessing: Spark-3.0.0
* Java: 11.0.7
* Python:3.0

# Environment Setup
## Install Java
```
$ sudo apt update
$ java -version
````
Ifjava is not installed, use following commands to install 
```
$ sudo apt get install default-jdk
$ java -version
openjdk version "11.0.7" 2020-04-14
OpenJDK Runtime Environment (build 11.0.7+10-post-Ubuntu-2ubuntu218.04)
OpenJDK 64-Bit Server VM (build 11.0.7+10-post-Ubuntu-2ubuntu218.04, mixed mode, sharing)
```
## Install and Setup Kafka
https://www.digitalocean.com/community/tutorials/how-to-install-apache-kafka-on-ubuntu-18-04

### Configure kafka and zookeeper
```
$ vi kafka/config/server.properties
````
Change the listeners as follows in the config file
```
listeners=PLAINTEXT://:9092
```
### Set up the zookeepers also listen to other than localhost
change the zookeeper.connect in the server.properties file
```
zookeeper.connect=:2181
```
## Install and setup Spark
### Creating a user for spark
```
$ sudo useradd spark -m
$ sudo passwd spark
$ su -l spark
```
### Install spark
```
$ wget https://downloads.apache.org/spark/spark-3.0.0/pyspark-3.0.0.tar.gz -o spark
$ tar zxvf spark-3.0.0.tgz
$ ln -s spark spark-3.0.0
```
### Add SPARK_HOME to your path
```
$ vi .profile
```
Add the following
```
export SPARK_HOME=/home/spark/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
```
### Start master and slave
```
$ start-master.sh
```
To start the slave check the name of the master in log_file
```
tail /home/spark/spark/logs/spark-spark-org.apache.spark.deploy.worker.Worker-1-playground.out
.....
.....
20/06/29 01:39:08 INFO Worker: Connecting to master playground.olqwded14uferdup0q0hjk0rtc.bx.internal.cloudapp.net:7077
```
Start the slave with 1 CPU and 2G Memory
```
$ start-slave.sh -c 1 -m 2G spark://playground.olqwded14uferdup0q0hjk0rtc.bx.internal.cloudapp.net:7077
```
To test it 
```
$ lynx http://127.0.0.1:8080
```
Or use the browser 
```
http://localhost:8080
http://<ipaddress>:8080
```
**Note** : If you are using cloud provider make sure you open the port 8080 for inbound access to all.

## Install and setup Druid / Imply
**Note** Imply is analtics platform built on top of druid.

### Creating a user for druid
```
$ sudo useradd druid -m
$ sudo passwd druid
$ su -l druid
```
### Install
https://docs.imply.io/on-prem/quickstart

#### Start Druid service
**Note**
Service start script checks for java 8.0 version if higher version and want to skip the check before start the service run the following
```
$ export IMPLY_SKIP_JAVA_CHECK=1
$ cd <IMPLY_INSTALL_DIR>
$ bin/supervise -c conf/supervise/quickstart.conf &
```
#### Check the service
http://localhost:9095 or
http://<ipaddress:9095

## Install and setup MongoDB
```
$ sudo apt-install -y mongodb
```
### Start and check the service
```
$ sudo systemctl status mongodb
$ sudo systemctl start mongodb
$ mongo --eval 'db.runCommand({ connectionStatus: 1 })'
MongoDB shell version v3.6.3
connecting to: mongodb://127.0.0.1:27017
MongoDB server version: 3.6.3
{
        "authInfo" : {
                "authenticatedUsers" : [ ],
                "authenticatedUserRoles" : [ ]
        },
        "ok" : 1
}

```







