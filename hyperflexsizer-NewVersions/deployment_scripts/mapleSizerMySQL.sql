# Converted with pg2mysql-1.9
# Converted on Tue, 18 Oct 2016 17:34:11 -0400
# Lightbox Technologies Inc. http://www.lightbox.ca

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone="+00:00";

CREATE TABLE auth_group (
    id int(11) NOT NULL,
    name varchar(80) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE auth_group_permissions (
    id int(11) NOT NULL,
    group_id int(11) NOT NULL,
    permission_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE auth_permission (
    id int(11) NOT NULL,
    name varchar(50) NOT NULL,
    content_type_id int(11) NOT NULL,
    codename varchar(100) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE auth_user (
    id int(11) NOT NULL AUTO_INCREMENT,
    password varchar(128) NOT NULL,
    last_login timestamp NOT NULL,
    is_superuser bool NOT NULL,
    username varchar(30) NOT NULL,
    first_name varchar(30) NOT NULL,
    last_name varchar(30) NOT NULL,
    email varchar(75) NOT NULL,
    is_staff bool NOT NULL,
    is_active bool NOT NULL,
    date_joined timestamp NOT NULL,
    PRIMARY KEY (id)
) ENGINE=MyISAM;

CREATE TABLE auth_user_groups (
    id int(11) NOT NULL,
    user_id int(11) NOT NULL,
    group_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE auth_user_user_permissions (
    id int(11) NOT NULL,
    user_id int(11) NOT NULL,
    permission_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE authtoken_token (
    `key` varchar(40) NOT NULL,
    created timestamp NOT NULL,
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_admin_log (
    id int(11) NOT NULL,
    action_time timestamp NOT NULL,
    object_id text,
    object_repr varchar(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id int(11),
    user_id int(11) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_content_type (
    id int(11) NOT NULL,
    name varchar(100) NOT NULL,
    app_label varchar(100) NOT NULL,
    model varchar(100) NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_migrations (
    id int(11) NOT NULL,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied timestamp NOT NULL
) ENGINE=MyISAM;

CREATE TABLE django_session (
    session_key varchar(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp NOT NULL
) ENGINE=MyISAM;

CREATE TABLE hyperconverged_node (
    id int(11) NOT NULL AUTO_INCREMENT,
    name text NOT NULL,
    node_json json NOT NULL,
    `type` varchar(200) NOT NULL,
    `status` bool NOT NULL,
    created_date timestamp NOT NULL,
    updated_date timestamp NOT NULL,
    PRIMARY KEY (id)
) ENGINE=MyISAM;

CREATE TABLE hyperconverged_part (
    id int(11) NOT NULL AUTO_INCREMENT,
    name text NOT NULL,
    part_json json NOT NULL,
    part_name text NOT NULL,
    `status` bool NOT NULL,
    created_date timestamp NOT NULL,
    updated_date timestamp NOT NULL,
    PRIMARY KEY (id)
) ENGINE=MyISAM;

CREATE TABLE hyperconverged_scenario (
    id int(11) NOT NULL AUTO_INCREMENT,
    name text NOT NULL,
    workload_json json NOT NULL,
    workload_result json NOT NULL,
    `status` bool NOT NULL,
    added_by_id int(11) NOT NULL,
    created_date timestamp NOT NULL,
    updated_date timestamp NOT NULL,
    cluster_json json,
    settings_json json,
    username text,
    PRIMARY KEY (id)
) ENGINE=MyISAM;


ALTER TABLE auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
ALTER TABLE auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
ALTER TABLE auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
ALTER TABLE auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);
ALTER TABLE auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);
ALTER TABLE django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
ALTER TABLE django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
ALTER TABLE django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
ALTER TABLE django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
ALTER TABLE `auth_group_permissions` ADD INDEX ( group_id ) ;
ALTER TABLE `auth_group_permissions` ADD INDEX ( permission_id ) ;
ALTER TABLE `auth_permission` ADD INDEX ( content_type_id ) ;
ALTER TABLE `auth_user_groups` ADD INDEX ( group_id ) ;
ALTER TABLE `auth_user_groups` ADD INDEX ( user_id ) ;
ALTER TABLE `auth_user_user_permissions` ADD INDEX ( permission_id ) ;
ALTER TABLE `auth_user_user_permissions` ADD INDEX ( user_id ) ;
ALTER TABLE `django_admin_log` ADD INDEX ( content_type_id ) ;
ALTER TABLE `django_admin_log` ADD INDEX ( user_id ) ;
ALTER TABLE `django_session` ADD INDEX ( expire_date ) ;
ALTER TABLE `hyperconverged_scenario` ADD INDEX ( added_by_id ) ;

