-- MySQL dump 10.13  Distrib 5.5.53, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: backup
-- ------------------------------------------------------
-- Server version	5.5.53-0ubuntu0.14.04.1

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
-- Table structure for table `auth_group`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `auth_group_permissions`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_0e939a4f` (`group_id`),
  KEY `auth_group_permissions_8373b171` (`permission_id`),
  CONSTRAINT `auth_group_permission_group_id_689710a9a73b7457_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group__permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_417f1b1c` (`content_type_id`),
  CONSTRAINT `auth__content_type_id_508cf46651277a81_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add permission',2,'add_permission'),(5,'Can change permission',2,'change_permission'),(6,'Can delete permission',2,'delete_permission'),(7,'Can add group',3,'add_group'),(8,'Can change group',3,'change_group'),(9,'Can delete group',3,'delete_group'),(10,'Can add user',4,'add_user'),(11,'Can change user',4,'change_user'),(12,'Can delete user',4,'delete_user'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add node',7,'add_node'),(20,'Can change node',7,'change_node'),(21,'Can delete node',7,'delete_node'),(22,'Can add part',8,'add_part'),(23,'Can change part',8,'change_part'),(24,'Can delete part',8,'delete_part'),(25,'Can add scenario',9,'add_scenario'),(26,'Can change scenario',9,'change_scenario'),(27,'Can delete scenario',9,'delete_scenario'),(28,'Can add token',10,'add_token'),(29,'Can change token',10,'change_token'),(30,'Can delete token',10,'delete_token');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime NOT NULL,
  `is_superuser` tinyint NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `is_staff` tinyint NOT NULL,
  `is_active` tinyint NOT NULL,
  `date_joined` datetime NOT NULL,
  `home_page_desc` boolean default true,
  `fixed_sizing_desc` boolean default true,
  `optimal_sizing_desc` boolean default true,
  `scenario_per_page` tinyint default 10,
  `language` varchar(20) NOT NULL default 'english',
  `accesslevel` tinyint DEFAULT '-1',
  `iops_access` boolean DEFAULT false,
  `home_disclaimer` date DEFAULT '01-01-0001',
  `price_list` varchar(15) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$12000$P5VaMOEuX45I$SxSU/rX9ZNqm5DKbyk1lzHncvzu2BoDnyDe+rID6ZIM=','2017-01-23 10:25:30',0,'admin','','','admin@admin.com',0,1,'2017-01-23 10:25:30');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_e8701ad4` (`user_id`),
  KEY `auth_user_groups_0e939a4f` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_33ac548dcf5f8e37_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_4b5ed4ffdb8fd9b0_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;



--
-- Table structure for table `auth_user_user_permissions`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_e8701ad4` (`user_id`),
  KEY `auth_user_user_permissions_8373b171` (`permission_id`),
  CONSTRAINT `auth_user_user_permissi_user_id_7f0938558328534a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `auth_user_u_permission_id_384b62483d7071f0_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `authtoken_token`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_1d10c57f535fb363_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
INSERT INTO `authtoken_token` VALUES ('2fae88b991ea4e4ccbe8603fa8d2273b1e113b08','2017-01-23 10:25:37',1);
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_417f1b1c` (`content_type_id`),
  KEY `django_admin_log_e8701ad4` (`user_id`),
  CONSTRAINT `django_admin_log_user_id_52fdd58701c5f563_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `djang_content_type_id_697914295151027a_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `django_content_type`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_45f3b1d93ec8c61c_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'log entry','admin','logentry'),(2,'permission','auth','permission'),(3,'group','auth','group'),(4,'user','auth','user'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'node','hyperconverged','node'),(8,'part','hyperconverged','part'),(9,'scenario','hyperconverged','scenario'),(10,'token','authtoken','token');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2017-01-23 10:17:01'),(2,'auth','0001_initial','2017-01-23 10:17:01'),(3,'admin','0001_initial','2017-01-23 10:17:02'),(4,'authtoken','0001_initial','2017-01-23 10:17:02'),(5,'hyperconverged','0001_initial','2017-01-23 10:17:02'),(6,'hyperconverged','0002_auto_20150505_1005','2017-01-23 10:17:02'),(7,'hyperconverged','0003_auto_20170123_1016','2017-01-23 10:17:03'),(8,'sessions','0001_initial','2017-01-23 10:17:03');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;



--
-- Table structure for table `hyperconverged_node`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hyperconverged_node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sort_index`int(11) NOT NULL DEFAULT 5000,
  `name` longtext NOT NULL,
  `node_json` json NOT NULL,
  `type` varchar(200) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `hercules_avail` boolean DEFAULT 0,
  `hx_boost_avail` boolean DEFAULT 0,
  `created_date` datetime NOT NULL,
  `updated_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `hyperconverged_part`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hyperconverged_part` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` longtext NOT NULL,
  `part_json` json NOT NULL,
  `part_name` longtext NOT NULL,
  `status` tinyint(1) NOT NULL,
  `created_date` datetime NOT NULL,
  `updated_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `hyperconverged_scenario`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hyperconverged_scenario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` longtext NOT NULL,
  `workload_json` json NOT NULL,
  `workload_result` json NOT NULL,
  `status` tinyint(1) NOT NULL,
  `created_date` datetime NOT NULL,
  `updated_date` datetime NOT NULL,
  `settings_json` json NOT NULL,
  `username` longtext NOT NULL,
  `sizing_type` VARCHAR(255) NOT NULL DEFAULT 'optimal',
  PRIMARY KEY (`id`),
  KEY `hyperconverged_scenario_0c5d7d4e` (`added_by_id`),
  CONSTRAINT `hyperconverged_scena_added_by_id_f0bba420770c72d_fk_auth_user_id` FOREIGN KEY (`added_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

CREATE TABLE `hyperconverged_sharedscenario` (
    `id` int(11) NOT NULL auto_increment,
    `scenario_id` int NOT NULL,
    `username` char(128) NOT NULL,
    `userid` char(128) NOT NULL,
    `acl` BOOL NOT NULL,
    `is_secure` boolean default false,
    PRIMARY KEY (`id`)
);

CREATE TABLE hyperconverged_specintdata (
    id int(11) NOT NULL AUTO_INCREMENT,
    model varchar(128) NOT NULL,
    speed FLOAT NOT NULL,
    cores INT NOT NULL,
    blended_core_2006 FLOAT(30),
    blended_core_2017 FLOAT(30),
	is_base_model BOOL,
    PRIMARY KEY (id),
    INDEX (model)
) ENGINE=MyISAM;

CREATE TABLE `hyperconverged_results` (
    `id` int not null auto_increment,
    `result_json` json,
    `settings_json` json,
    `created_date` datetime,
    `scenario_id` int,
    `name` text,
    `error_json` json DEFAULT '{}'
    PRIMARY KEY (`id`)
);

CREATE TABLE `hyperconverged_thresholds` (
    `id` int not null auto_increment,
    `threshold_key` char(15),
    `workload_type` char(11),
    `threshold_value` tinyint,
    `threshold_category` tinyint,
    PRIMARY KEY (`id`)
);

CREATE TABLE `hyperconverged_feature_permission` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `feature` varchar(128) NOT NULL,
    `access_level` tinyint NOT NULL,
    PRIMARY KEY (`id`)
);

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-23  2:30:02

CREATE TABLE `hyperconverged_iopsconvfactor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `threshold` int(11) NOT NULL,
  `iops_conv_factor` int(11) NOT NULL,
  `replication_factor` varchar(10) NOT NULL,
  `workload_type` varchar(30) NOT NULL,
  `part_name` varchar(50) NOT NULL,
  `hypervisor` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hyperconverged_iopsconvfactor_threshold_52c97b8c3975ecc8_uniq` (`threshold`,`workload_type`,`part_name`,`replication_factor`,`hypervisor`)
) ENGINE=InnoDB AUTO_INCREMENT=2254 DEFAULT CHARSET=latin1;

CREATE TABLE `hyperconverged_laeusers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

CREATE TABLE `hx_perf_numbers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_type` varchar(10),
  `hypervisor` tinyint(1),
  `wl_type` varchar(30),
  `threshold` int(11),
  `node_substring` varchar(10),
  `ssd_string` varchar(30),
  `replication_factor` varchar(10),
  `iops_type` varchar(50),
  `iops_value` int(11),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;

CREATE TABLE `hyperconverged_rules` (
  `rule_id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_json` json,
  PRIMARY KEY (`rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `hyperconverged_fixedresults` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `result_json` JSON NULL,
  `error_json` JSON NULL,
  `cluster_name` VARCHAR(45) NULL,
  `scenario_id` INT NOT NULL,
  `settings_json` json NOT NULL,
  `created_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `hyperconverged_ccwdata` (
    `id` int(11) NOT NULL auto_increment,
    `product_id` char(128) NOT NULL,
    `product_path` char(128) NOT NULL,
    `product_reference` char(128) NOT NULL,
	`product_parent` char(128),
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `hyperconverged_uploadbomexcelinfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `bom_input_json` JSON NOT NULL,
  `username` varchar(30) NOT NULL,
  `is_completed` boolean default false,
  `transaction_datetime` TIMESTAMP default current_timestamp,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `hyperconverged_estimatedetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scenario_id` int(11) NOT NULL,
  `scenario_name` varchar(100) NOT NULL,
  `estimate_id` varchar(70) NOT NULL,
  `estimate_name` varchar(100) NOT NULL,
  `estimate_response` varchar(200) NOT NULL,
  `is_updated` tinyint(1) DEFAULT '0',
  `created_datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;

CREATE TABLE `hyperconverged_apidetails` (
  `api_id` int AUTO_INCREMENT,
  `scenario_id` INT NOT NULL,
  `api_name` INT NOT NULL DEFAULT 0,
  `api_token` VARCHAR(30) NOT NULL UNIQUE,
  `is_claimed` boolean default false,
  `transaction_datetime` TIMESTAMP default current_timestamp,
  PRIMARY KEY (`api_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
