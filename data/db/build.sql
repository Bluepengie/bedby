CREATE TABLE IF NOT EXISTS exp (
  UserID integer PRIMARY KEY,
  XP integer DEFAULT 0,
  Level integer DEFAULT 0,
  XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS starboard (
  RootMessageID integer PRIMARY KEY,
  StarMessageID integer,
  Stars integer DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dinkboard (
  UserID integer PRIMARY KEY,
  DinkOut integer DEFAULT 0,
  DinkIn integer DEFAULT 0
);