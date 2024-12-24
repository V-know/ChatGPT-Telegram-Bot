create database ai;

CREATE TABLE `users` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `nick_name` varchar(128) DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `level` tinyint DEFAULT NULL,
  `parse_mode` varchar(10) DEFAULT 'Markdown',
  `system_content` varchar(1024) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=132 DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_user_id ON records(user_id);

CREATE TABLE `records` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint DEFAULT NULL,
  `role` varchar(50) NOT NULL,
  `content` text NOT NULL,
  `tokens` int DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `reset_at` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1974 DEFAULT CHARSET=utf8mb4;

create index idx_user_id on users (user_id);

create table image_requests
(
    id         int auto_increment
        primary key,
    user_id    bigint      not null,
    created_at datetime    not null,
    prompt     text        not null,
    image_name varchar(64) null,
    updated_at timestamp   null,
    constraint image_requests_ibfk_1
        foreign key (user_id) references users (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1974 DEFAULT CHARSET=utf8mb4;

create index user_id on image_requests (user_id);