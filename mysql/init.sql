CREATE DATABASE IF NOT EXISTS FastAPIPractical;
USE FastAPIPractical;

-- Create Role table
CREATE TABLE role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Insert predefined roles
INSERT INTO role (name) VALUES ('Admin'), ('Normal User');

-- Create User table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profilepic VARCHAR(255),
    name VARCHAR(100) NOT NULL,
    cellnumber VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    roleId INT NOT NULL,
    deletedAt DATETIME DEFAULT NULL,
    created DATETIME NOT NULL,
    modified DATETIME NOT NULL,
    FOREIGN KEY (roleId) REFERENCES role(id)
);

-- Create AccessToken table
CREATE TABLE accesstoken (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token TEXT NOT NULL,
    ttl INT NOT NULL,
    userId INT NOT NULL,
    created DATETIME NOT NULL,
    FOREIGN KEY (userId) REFERENCES user(id)
);
