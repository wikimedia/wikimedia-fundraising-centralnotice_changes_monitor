-- Create tables used by this library/scripts. See README.md for details.
CREATE TABLE pages_to_monitor (
  id               INT           UNSIGNED AUTO_INCREMENT,
  title            VARCHAR(256)  NOT NULL,
  checked_revision INT           UNSIGNED NOT NULL,

  PRIMARY KEY (id),
  UNIQUE KEY (title),
  INDEX (title)
) DEFAULT CHARACTER SET = utf8 ENGINE = InnoDB;
