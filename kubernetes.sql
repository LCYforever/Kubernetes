/*
Navicat MySQL Data Transfer

Source Server         : deepnex
Source Server Version : 50720
Source Host           : localhost:3306
Source Database       : k8s

Target Server Type    : MYSQL
Target Server Version : 50720
File Encoding         : 65001

Date: 2018-05-04 21:44:07
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `alembic_version`
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('bcc6d2d2434f');

-- ----------------------------
-- Table structure for `image`
-- ----------------------------
DROP TABLE IF EXISTS `image`;
CREATE TABLE `image` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of image
-- ----------------------------
INSERT INTO `image` VALUES ('1', '192.168.80.138:5000/ubuntu:16.04');

-- ----------------------------
-- Table structure for `instance`
-- ----------------------------
DROP TABLE IF EXISTS `instance`;
CREATE TABLE `instance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `instance_name` varchar(128) NOT NULL,
  `image_id` int(11) DEFAULT NULL,
  `cpu_num` int(11) DEFAULT NULL,
  `memory_num` int(11) DEFAULT NULL,
  `container_num` int(11) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `image_id` (`image_id`),
  CONSTRAINT `instance_ibfk_1` FOREIGN KEY (`image_id`) REFERENCES `image` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of instance
-- ----------------------------

-- ----------------------------
-- Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `auth_level` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('1', 'wurun', '123456', '1');
INSERT INTO `user` VALUES ('2', 'gangan', 'pbkdf2:sha256:50000$zuCC2iru$31ffa30a5d9b435d6990ee871f57dffd12012fc6a7b7bb3e8858631ca276d883', '0');
