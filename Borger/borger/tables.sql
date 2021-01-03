CREATE TABLE BorgerUser (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,
    CreatedAt TEXT NOT NULL
); 

CREATE TABLE Address (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Address TEXT NOT NULL,
    CreatedAt TEXT NOT NULL,
    BorgerUserId INTEGER NOT NULL, 
    IsValid BOOLEAN NOT NULL CHECK (IsValid IN (0,1)),
    FOREIGN KEY (BorgerUserId) references BorgerUser(Id) ON DELETE CASCADE
);

-- drop table Address;
-- drop table BorgerUser;

