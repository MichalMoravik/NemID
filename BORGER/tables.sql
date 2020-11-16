CREATE TABLE BorgerUser (
    Id INTEGER PRIMARY KEY,
    UserId TEXT NOT NULL,
    CreatedAt DATE
) 


CREATE TABLE Address (
        Id INTEGER PRIMARY KEY,
        Address text,
        CreatedAt DATE,
        isvalid INTEGER,
        BorgerUserId TEXT NOT NULL, 
      CONSTRAINT FK_BorgerUserId  FOREIGN KEY (BorgerUserId) REFERENCES BorgerUser (UserId) ON DELETE CASCADE
) 

INSERT INTO BorgerUser(UserId, CreatedAt) VALUES ('4dcb3005-c58b-4727-ab04-405b81795cd9', '2020-11-16 22:45:36.185119')
INSERT INTO Address(Address, CreatedAt, isvalid, BorgerUserId) VALUES ('Katrinedal 16', datetime('now'), 1,12)

DELETE from BorgerUser 
where UserId = 12


drop table Address
drop table BorgerUser

