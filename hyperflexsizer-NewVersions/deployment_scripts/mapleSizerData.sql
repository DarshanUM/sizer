-- MySQL dump 10.13  Distrib 5.7.16, for Linux (x86_64)
--
-- Host: localhost    Database: maplesizer
-- ------------------------------------------------------
-- Server version	5.7.16-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add permission',2,'add_permission'),(5,'Can change permission',2,'change_permission'),(6,'Can delete permission',2,'delete_permission'),(7,'Can add group',3,'add_group'),(8,'Can change group',3,'change_group'),(9,'Can delete group',3,'delete_group'),(10,'Can add user',4,'add_user'),(11,'Can change user',4,'change_user'),(12,'Can delete user',4,'delete_user'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add node',7,'add_node'),(20,'Can change node',7,'change_node'),(21,'Can delete node',7,'delete_node'),(22,'Can add part',8,'add_part'),(23,'Can change part',8,'change_part'),(24,'Can delete part',8,'delete_part'),(25,'Can add scenario',9,'add_scenario'),(26,'Can change scenario',9,'change_scenario'),(27,'Can delete scenario',9,'delete_scenario'),(28,'Can add node',10,'add_node'),(29,'Can change node',10,'change_node'),(30,'Can delete node',10,'delete_node'),(31,'Can add part',11,'add_part'),(32,'Can change part',11,'change_part'),(33,'Can delete part',11,'delete_part'),(34,'Can add scenario',12,'add_scenario'),(35,'Can change scenario',12,'change_scenario'),(36,'Can delete scenario',12,'delete_scenario'),(37,'Can add node',13,'add_node'),(38,'Can change node',13,'change_node'),(39,'Can delete node',13,'delete_node'),(40,'Can add part',14,'add_part'),(41,'Can change part',14,'change_part'),(42,'Can delete part',14,'delete_part'),(43,'Can add scenario',15,'add_scenario'),(44,'Can change scenario',15,'change_scenario'),(45,'Can delete scenario',15,'delete_scenario'),(46,'Can add token',16,'add_token'),(47,'Can change token',16,'change_token'),(48,'Can delete token',16,'delete_token');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$12000$wvh13H1oNq1s$vyafmUr9ytEH88EPTN6DQgrpLcgzqu9nq6/FxAsc7TY=','2015-07-02 10:32:30',0,'test','','','test@test.com',0,1,'2015-07-02 10:32:30'),(3,'pbkdf2_sha256$12000$i2fukjkc7asO$prYffAz9cG0/BcxU/JCy9luPuCcSyCiFpWgMa1TV4n8=','2016-03-24 09:21:12',0,'admin','','','admin@admin.com',0,1,'2016-03-24 09:21:12'),(4,'pbkdf2_sha256$12000$69QigBGFZ22B$WSO9bLRMXSKKKXeAahIexf2k9OWjUNjD+ZkkmRdPCSI=','2016-11-18 00:09:56',0,'testUser','','','',0,1,'2016-11-18 00:09:56'),(5,'pbkdf2_sha256$12000$LecF0351J6K6$QCzmYD5fJyaVcprHXk4Wa9MZ4bxQ0H5R+kdDy5z4Lfg=','2016-11-18 00:12:30',0,'michael','','','',0,1,'2016-11-18 00:12:30');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
INSERT INTO `authtoken_token` VALUES ('03011f56614a48b7e76642149b9e1e7ecad55fa2','2016-11-16 04:26:47',3);
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `backupstorage_node`
--

LOCK TABLES `backupstorage_node` WRITE;
/*!40000 ALTER TABLE `backupstorage_node` DISABLE KEYS */;
/*!40000 ALTER TABLE `backupstorage_node` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `backupstorage_part`
--

LOCK TABLES `backupstorage_part` WRITE;
/*!40000 ALTER TABLE `backupstorage_part` DISABLE KEYS */;
/*!40000 ALTER TABLE `backupstorage_part` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `backupstorage_scenario`
--

LOCK TABLES `backupstorage_scenario` WRITE;
/*!40000 ALTER TABLE `backupstorage_scenario` DISABLE KEYS */;
/*!40000 ALTER TABLE `backupstorage_scenario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'log entry','admin','logentry'),(2,'permission','auth','permission'),(3,'group','auth','group'),(4,'user','auth','user'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'node','storage','node'),(8,'part','storage','part'),(9,'scenario','storage','scenario'),(10,'node','hyperconverged','node'),(11,'part','hyperconverged','part'),(12,'scenario','hyperconverged','scenario'),(13,'node','backupstorage','node'),(14,'part','backupstorage','part'),(15,'scenario','backupstorage','scenario'),(16,'token','authtoken','token');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2016-03-24 09:19:30'),(2,'auth','0001_initial','2016-03-24 09:19:31'),(3,'admin','0001_initial','2016-03-24 09:19:31'),(4,'authtoken','0001_initial','2016-03-24 09:19:31'),(5,'backupstorage','0001_initial','2016-03-24 09:19:31'),(6,'hyperconverged','0001_initial','2016-03-24 09:19:32'),(7,'hyperconverged','0002_auto_20150505_1005','2016-03-24 09:19:32'),(8,'sessions','0001_initial','2016-03-24 09:19:33'),(9,'storage','0001_initial','2016-03-24 09:19:33'),(10,'storage','0002_auto_20150713_0718','2016-03-24 09:19:33');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `hyperconverged_node`
--

LOCK TABLES `hyperconverged_node` WRITE;
/*!40000 ALTER TABLE `hyperconverged_node` DISABLE KEYS */;
INSERT INTO `hyperconverged_node` VALUES (1,'HX-220-SP-BE1','{\"vendor\": \"CISCO\", \"name\": \"HX-220-SP-BE1\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2609v4\"], \"ram_slots\": [8, 10, 12, 14, 16, 18, 20, 22, 24], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [6], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 16560, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":48,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.6},\"gpu_slots\":[0],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(2,'HX-220-SP-BE2','{\"vendor\": \"CISCO\", \"name\": \"HX-220-SP-BE2\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2630v4\"], \"ram_slots\": [8, 10, 12, 14, 16, 18, 20, 22, 24], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [6], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 26780, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":48,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.6},\"gpu_slots\":[0],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(3,'HX-220-SP-BV1','{\"vendor\": \"CISCO\", \"name\": \"HX-220-SP-BV1\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2650v4\"], \"ram_slots\": [12, 14, 16, 18, 20, 22, 24], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [6], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 23120, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":48,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.6},\"gpu_slots\":[0],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(4,'HX-220-SP-BP1','{\"vendor\": \"CISCO\", \"name\": \"HX-220-SP-BP1\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2690v4\"], \"ram_slots\": [16, 18, 20, 22, 24], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [6], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 27060, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":48,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.6},\"gpu_slots\":[0],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(5,'HX-240-SP-BE1','{\"vendor\": \"CISCO\", \"name\": \"HX-240-SP-BE1\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2609v4\"], \"ram_slots\": [8, 10, 12, 14, 16, 18, 20, 22, 24], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [11], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"1600_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 25560, \"rack_space\": 2, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":72,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.85},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(6,'HX-240-SP-BE2','{\"vendor\": \"CISCO\", \"name\": \"HX-240-SP-BE2\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2630v4\"], \"ram_slots\": [8, 10, 12, 14, 16, 18, 20, 22, 24], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [11], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"1600_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 33980, \"rack_space\": 2, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":72,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.85},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(7,'HX-240-SP-BV1','{\"vendor\": \"CISCO\", \"name\": \"HX-240-SP-BV1\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2650v4\"], \"ram_slots\": [12, 14, 16, 18, 20, 22, 24], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [15], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"1600_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 33220, \"rack_space\": 2, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":72,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.85},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(8,'HX-240-SP-BP1','{\"vendor\": \"CISCO\", \"name\": \"HX-240-SP-BP1\", \"type\": \"configurable\", \"subtype\":\"hyperconverged\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2690v4\"], \"ram_slots\": [16, 18, 20, 22, 24], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [15], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [1], \"ssd_options\": [\"1600_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 31404, \"rack_space\": 2, \"power\": 120, \"btu\": 2200, \"status\": true,\"iops_conversion_factor\":{\"VDI\":1,\"VM\":1,\"DB\":1},\"static_overhead\":{\"CPU\":4,\"RAM\":72,\"HDD\":8},\"node_cache_factor\":{\"SSD\":0.85},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(9,'B200-M4-BB1','{\"vendor\": \"CISCO\", \"name\": \"B200-M4-BB1\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2609v4\"], \"ram_slots\": [4], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[0,1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(10,'B200-M4-BS1','{\"vendor\": \"CISCO\", \"name\": \"B200-M4-BS1\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2630v4\"], \"ram_slots\": [4], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(11,'B200-M4-BA1','{\"vendor\": \"CISCO\", \"name\": \"B200-M4-BA1\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2690v4\"], \"ram_slots\": [8], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(12,'B200-M4-BA2','{\"vendor\": \"CISCO\", \"name\": \"B200-M4-BA2\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2650v4\"], \"ram_slots\": [8], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(13,'C220-M4-B-B1','{\"vendor\": \"CISCO\", \"name\": \"C220-M4-B-B1\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2609v4\"], \"ram_slots\": [4], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(14,'C220-M4-B-S1','{\"vendor\": \"CISCO\", \"name\": \"C220-M4-B-S1\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2630v4\"], \"ram_slots\": [4], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(15,'C220-M4-B-A2','{\"vendor\": \"CISCO\", \"name\": \"C220-M4-B-A2\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2650v4\"], \"ram_slots\": [8], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[1],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(16,'C240-M4-B-S1','{\"vendor\": \"CISCO\", \"name\": \"C240-M4-B-S1\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2630v4\"], \"ram_slots\": [8], \"ram_options\": [\"16GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[2],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45'),(17,'C240-M4-B-A2','{\"vendor\": \"CISCO\", \"name\": \"C240-M4-B-A2\", \"type\": \"configurable\", \"subtype\":\"compute\",\"cpu_socket_count\": [2], \"cpu_options\": [\"E5-2650v4\"], \"ram_slots\": [8], \"ram_options\": [\"32GB_DDR4\"], \"hdd_slots\": [0], \"hdd_options\": [\"1.2TB_1\"], \"ssd_slots\": [0], \"ssd_options\": [\"480_GB_SSD\"], \"network_throughput\": 25000, \"base_price\": 6000, \"rack_space\": 1, \"power\": 120, \"btu\": 2200, \"status\": true,\"node_cache_factor\":{\"SSD\":1},\"gpu_slots\":[2],\"gpu_options\":[\"TEST_GPU\"]}','',1,'2015-07-03 05:51:45','2015-07-03 05:51:45');
/*!40000 ALTER TABLE `hyperconverged_node` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `hyperconverged_part`
--

LOCK TABLES `hyperconverged_part` WRITE;
/*!40000 ALTER TABLE `hyperconverged_part` DISABLE KEYS */;
INSERT INTO `hyperconverged_part` VALUES (1,'E5-2609v4','{\"name\": \"E5-2609v4\", \"capacity\": 8, \"unit_price\": 0, \"description\": \"Intel Xeon Processor E5-2609 v4, 8 cores, 1.7GHz\", \"frequency\": \"1.7\", \"l3_cache\": \"15\", \"tdp\": \"85\", \"speclnt\": \"0\"}','',1,'2015-07-03 05:55:41','2015-07-03 05:55:41'),(2,'E5-2630v4','{\"name\": \"E5-2630v4\", \"capacity\": 10, \"unit_price\": 0, \"description\": \"Intel Xeon Processor E5-2630 v4, 10 cores, 2.2GHz\", \"frequency\": \"2.2\", \"l3_cache\": \"30\", \"tdp\": \"120\", \"speclnt\": \"0\"}','',1,'2015-07-03 05:55:57','2015-07-03 05:55:57'),(3,'E5-2650v4','{\"name\": \"E5-2650v4\", \"capacity\": 12, \"unit_price\": 0, \"description\": \"Intel Xeon Processor E5-2650 v4, 12 cores, 2.2GHz\", \"frequency\": \"2.2\", \"l3_cache\": \"30\", \"tdp\": \"135\", \"speclnt\": \"0\"}','',1,'2015-07-03 05:56:12','2015-07-03 05:56:12'),(4,'E5-2690v4','{\"name\": \"E5-2690v4\", \"capacity\": 14, \"unit_price\": 0, \"description\": \"Intel Xeon Processor E5-2690 v4, 14 cores, 2.60GHz\", \"frequency\": \"2.6\", \"l3_cache\": \"40\", \"tdp\": \"135\", \"speclnt\": \"0\"}','',1,'2015-07-03 05:56:29','2015-07-03 05:56:28'),(5,'16GB_DDR4','{\"name\": \"16GB_DDR4\", \"capacity\": 16, \"unit_price\": 430, \"description\": \"DDR4 RAM\"}','',1,'2015-07-03 06:02:04','2015-07-03 06:02:04'),(6,'32GB_DDR4','{\"name\": \"32GB_DDR4\", \"capacity\": 32, \"unit_price\": 1090, \"description\": \"DDR4 RAM\"}','',1,'2015-07-03 06:02:24','2015-07-03 06:02:24'),(7,'1TB_1','{\"name\": \"1.2TB_1\", \"capacity\": 1200, \"unit_price\": 0, \"description\": \"Seagate Constellation 1.2 TB 2.5in SATA 6 Gb/s HDD\", \"encryption\": \"No\", \"iops_per_disk\": 200}','',1,'2015-07-03 06:02:49','2015-07-03 06:02:48'),(8,'480_GB_SSD','{\"name\": \"480_GB_SSD\", \"capacity\": 480, \"unit_price\": 0, \"description\": \"Intel SSD DC S3500 Series (480GB, 2.5in SATA 6Gb/s, 20nm, MLC)\", \"iops_per_disk\":20000}','',1,'2015-07-03 06:04:27','2015-07-03 06:04:27'),(9,'1600_GB_SSD','{\"name\": \"1600_GB_SSD\", \"capacity\": 1600, \"unit_price\": 0, \"description\": \"Intel SSD DC S3500 Series (1.6TB, 2.5in SATA 6Gb/s, 20nm, MLC)\", \"iops_per_disk\":40000}','',1,'2015-07-03 06:05:44','2015-07-03 06:05:44'),(10,'TEST_GPU','{\"name\": \"TEST_GPU\", \"capacity\": 20, \"unit_price\": 0, \"description\": \"NVIDIA Grid K1\"}','',1,'2015-07-03 06:05:44','2015-07-03 06:05:44');
/*!40000 ALTER TABLE `hyperconverged_part` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `hyperconverged_scenario`
--

LOCK TABLES `hyperconverged_scenario` WRITE;
/*!40000 ALTER TABLE `hyperconverged_scenario` DISABLE KEYS */;
INSERT INTO `hyperconverged_scenario` VALUES (69,'Test2','{\"settings_json\": {\"threshold\": 2, \"fault_tolerance\": 0, \"heterogenous\": false}, \"wl_list\": [{\"num_vms\": 450, \"vcpus_per_vm\": 1, \"dedupe_factor\": 20, \"profile_type\": \"Task Worker\", \"wl_name\": \"VM_1\", \"wl_type\": \"VM\", \"vcpus_per_core\": 3, \"snapshots\": 5, \"working_set\": 10, \"base_image_size\": 20, \"ram_per_vm\": 2, \"replication_factor\": 0, \"provisioning_type\": \"View Linked Clones\", \"gpu_users\": 0, \"compression_factor\": 0, \"disk_per_vm\": 40, \"avg_iops_per_vm\": 30}, {\"avg_iops_per_desktop\": 30, \"gold_image_size\": 20, \"dedupe_factor\": 20, \"profile_type\": \"Task Worker\", \"wl_name\": \"VDI_1\", \"wl_type\": \"VDI\", \"vcpus_per_core\": 3, \"working_set\": 10, \"disk_per_desktop\": 40, \"num_desktops\": 450, \"ram_per_desktop\": 2, \"replication_factor\": 0, \"provisioning_type\": \"View Linked Clones\", \"vcpus_per_desktop\": 1, \"gpu_users\": 0, \"compression_factor\": 0}], \"model_list\": [], \"name\": \"vdi\", \"model_choice\": \"None\"}','[{\"clusters\": [{\"Utilization\": [{\"node_val\": 168, \"units\": \"Cores\", \"tag_name\": \"CPU\", \"utilization\": 89.0, \"workload_val\": 150}, {\"node_val\": 3080, \"units\": \"GB\", \"tag_name\": \"RAM\", \"utilization\": 29.0, \"workload_val\": 900}, {\"node_val\": 115920, \"units\": \"GB\", \"tag_name\": \"HDD\", \"utilization\": 19.0, \"workload_val\": 23040}, {\"node_val\": 9449, \"units\": \"GB\", \"tag_name\": \"SSD\", \"utilization\": 24.0, \"workload_val\": 2305}, {\"node_val\": 280000, \"units\": \"K\", \"tag_name\": \"IOPS\", \"utilization\": 4.0, \"workload_val\": 13500}, {\"node_val\": 140, \"units\": \"Users\", \"tag_name\": \"GPU Users\", \"utilization\": 0.0, \"workload_val\": 0}], \"settings\": {\"Threshold\": 2, \"Fault_Tolerance\": 0, \"Heterogenous\": false, \"Replication_Factor\": 0}, \"WL_List\": [{\"num_vms\": 450, \"vcpus_per_vm\": 1, \"dedupe_factor\": 20, \"profile_type\": \"Task Worker\", \"replication_mult\": 1, \"wl_name\": \"VM_1\", \"wl_type\": \"VM\", \"vcpus_per_core\": 3, \"snapshots\": 5, \"working_set\": 10, \"base_image_size\": 20, \"ram_per_vm\": 2, \"replication_factor\": 0, \"provisioning_type\": \"View Linked Clones\", \"gpu_users\": 0, \"compression_factor\": 0, \"disk_per_vm\": 40, \"avg_iops_per_vm\": 30}], \"node_info\": [{\"model_details\": {\"cpu_price\": 0, \"gpu_slots\": 1, \"cpu_part\": \"E5-2690v4\", \"cores_per_cpu\": 14, \"ssd_part\": \"1600_GB_SSD\", \"ram_size\": 32, \"cpu_cores\": 28, \"total_ram_size\": 512, \"GPU_USERS\": 20, \"type\": \"configurable\", \"cpu_socket_count\": 2, \"opex_per_year\": 42882, \"hdd_slots\": 15, \"hdd_size\": 1.2, \"power\": 120, \"hdd_part\": \"1.2TB_1\", \"rack_space\": 2, \"node_base_price\": 31404, \"node_description\": [\"2xIntel Xeon Processor E5-2690 v4, 14 cores, 2.60GHz\", \"512 GB DDR4 RAM\", \"15x1.2 TB 2.5\\\" HDD\", \"1x1600 GB 2.5\\\" SSD\", \"40000 IOPS @4K block size \", \"1 NVIDIA Grid K1\"], \"base_price\": 48844, \"name\": \"HX-240-SP-BP1\", \"ssd_slots\": 1, \"ram_price\": 1090, \"ssd_price\": 0, \"ssd_size\": 1600, \"subtype\": \"hyperconverged\", \"ram_part\": \"32GB_DDR4\", \"ram_slots\": 16, \"hdd_price\": 0}, \"display_name\": \"Cluster_1\", \"num_nodes\": 7}], \"pricing\": [{\"value\": [{\"highlight\": \"True\", \"tag_name\": \"Total\", \"tag_val\": 470554.0}, {\"highlight\": \"False\", \"tag_name\": \"Capex\", \"tag_val\": 341908}, {\"highlight\": \"False\", \"tag_name\": \"Opex for 3 years\", \"tag_val\": 128646}], \"label\": \"Summary\"}, {\"value\": [{\"tag_name\": \"Capex\", \"tag_val\": 341908}, {\"tag_name\": \"Server\", \"tag_val\": 341908}, {\"tag_name\": \"Network\", \"tag_val\": 0}], \"label\": \"Capex\"}, {\"value\": [{\"highlight\": \"True\", \"tag_name\": \"Opex\", \"tag_val\": 42882}, {\"highlight\": \"False\", \"tag_name\": \"Support\", \"tag_val\": 14312}, {\"highlight\": \"False\", \"tag_name\": \"Maintenance\", \"tag_val\": 17640}, {\"highlight\": \"False\", \"tag_name\": \"Facilities\", \"tag_val\": 10930}], \"label\": \"Annual Opex\"}], \"num_gpu\": 0}, {\"Utilization\": [{\"node_val\": 168, \"units\": \"Cores\", \"tag_name\": \"CPU\", \"utilization\": 89.0, \"workload_val\": 150}, {\"node_val\": 3080, \"units\": \"GB\", \"tag_name\": \"RAM\", \"utilization\": 29.0, \"workload_val\": 900}, {\"node_val\": 115920, \"units\": \"GB\", \"tag_name\": \"HDD\", \"utilization\": 12.0, \"workload_val\": 14420}, {\"node_val\": 9449, \"units\": \"GB\", \"tag_name\": \"SSD\", \"utilization\": 22.0, \"workload_val\": 2161}, {\"node_val\": 280000, \"units\": \"K\", \"tag_name\": \"IOPS\", \"utilization\": 4.0, \"workload_val\": 13500}, {\"node_val\": 140, \"units\": \"Users\", \"tag_name\": \"GPU Users\", \"utilization\": 0.0, \"workload_val\": 0}], \"settings\": {\"Threshold\": 2, \"Fault_Tolerance\": 0, \"Heterogenous\": false, \"Replication_Factor\": 0}, \"WL_List\": [{\"avg_iops_per_desktop\": 30, \"gold_image_size\": 20, \"dedupe_factor\": 20, \"profile_type\": \"Task Worker\", \"replication_mult\": 1, \"wl_name\": \"VDI_1\", \"wl_type\": \"VDI\", \"vcpus_per_core\": 3, \"working_set\": 10, \"disk_per_desktop\": 40, \"num_desktops\": 450, \"ram_per_desktop\": 2, \"replication_factor\": 0, \"provisioning_type\": \"View Linked Clones\", \"vcpus_per_desktop\": 1, \"gpu_users\": 0, \"compression_factor\": 0}], \"node_info\": [{\"model_details\": {\"cpu_price\": 0, \"gpu_slots\": 1, \"cpu_part\": \"E5-2690v4\", \"cores_per_cpu\": 14, \"ssd_part\": \"1600_GB_SSD\", \"ram_size\": 32, \"cpu_cores\": 28, \"total_ram_size\": 512, \"GPU_USERS\": 20, \"type\": \"configurable\", \"cpu_socket_count\": 2, \"opex_per_year\": 42882, \"hdd_slots\": 15, \"hdd_size\": 1.2, \"power\": 120, \"hdd_part\": \"1.2TB_1\", \"rack_space\": 2, \"node_base_price\": 31404, \"node_description\": [\"2xIntel Xeon Processor E5-2690 v4, 14 cores, 2.60GHz\", \"512 GB DDR4 RAM\", \"15x1.2 TB 2.5\\\" HDD\", \"1x1600 GB 2.5\\\" SSD\", \"40000 IOPS @4K block size \", \"1 NVIDIA Grid K1\"], \"base_price\": 48844, \"name\": \"HX-240-SP-BP1\", \"ssd_slots\": 1, \"ram_price\": 1090, \"ssd_price\": 0, \"ssd_size\": 1600, \"subtype\": \"hyperconverged\", \"ram_part\": \"32GB_DDR4\", \"ram_slots\": 16, \"hdd_price\": 0}, \"display_name\": \"Cluster_2\", \"num_nodes\": 7}], \"pricing\": [{\"value\": [{\"highlight\": \"True\", \"tag_name\": \"Total\", \"tag_val\": 470554.0}, {\"highlight\": \"False\", \"tag_name\": \"Capex\", \"tag_val\": 341908}, {\"highlight\": \"False\", \"tag_name\": \"Opex for 3 years\", \"tag_val\": 128646}], \"label\": \"Summary\"}, {\"value\": [{\"tag_name\": \"Capex\", \"tag_val\": 341908}, {\"tag_name\": \"Server\", \"tag_val\": 341908}, {\"tag_name\": \"Network\", \"tag_val\": 0}], \"label\": \"Capex\"}, {\"value\": [{\"highlight\": \"True\", \"tag_name\": \"Opex\", \"tag_val\": 42882}, {\"highlight\": \"False\", \"tag_name\": \"Support\", \"tag_val\": 14312}, {\"highlight\": \"False\", \"tag_name\": \"Maintenance\", \"tag_val\": 17640}, {\"highlight\": \"False\", \"tag_name\": \"Facilities\", \"tag_val\": 10930}], \"label\": \"Annual Opex\"}], \"num_gpu\": 0}], \"summary_info\": {\"capex\": 683816, \"opex\": 85764, \"aggr_utilization\": [{\"node_val\": 336, \"units\": \"Cores\", \"tag_name\": \"CPU\", \"workload_val\": 300, \"utilization\": 89.0}, {\"node_val\": 6160, \"units\": \"GB\", \"tag_name\": \"RAM\", \"workload_val\": 1800, \"utilization\": 29.0}, {\"node_val\": 231840, \"units\": \"GB\", \"tag_name\": \"HDD\", \"workload_val\": 37460, \"utilization\": 16.0}, {\"node_val\": 18898, \"units\": \"GB\", \"tag_name\": \"SSD\", \"workload_val\": 4466, \"utilization\": 23.0}, {\"node_val\": 560000, \"units\": \"K\", \"tag_name\": \"IOPS\", \"workload_val\": 27000, \"utilization\": 4.0}, {\"node_val\": 280, \"units\": \"Users\", \"tag_name\": \"GPU Users\", \"workload_val\": 0, \"utilization\": 0.0}], \"num_nodes\": 14}}]',1,3,'2016-10-04 22:45:51','2016-12-02 05:56:29','{\"threshold\": 2, \"account\": \"test\", \"fault_tolerance\": 0, \"heterogenous\": false, \"deal_id\": \"test2\"}',NULL,'admin');
/*!40000 ALTER TABLE `hyperconverged_scenario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `storage_node`
--

LOCK TABLES `storage_node` WRITE;
/*!40000 ALTER TABLE `storage_node` DISABLE KEYS */;
/*!40000 ALTER TABLE `storage_node` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `storage_part`
--

LOCK TABLES `storage_part` WRITE;
/*!40000 ALTER TABLE `storage_part` DISABLE KEYS */;
/*!40000 ALTER TABLE `storage_part` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `storage_scenario`
--

LOCK TABLES `storage_scenario` WRITE;
/*!40000 ALTER TABLE `storage_scenario` DISABLE KEYS */;
/*!40000 ALTER TABLE `storage_scenario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-01 21:55:54
