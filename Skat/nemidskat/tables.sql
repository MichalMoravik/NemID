CREATE TABLE SkatUser (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INT,
    CreatedAt DATETIME,
    IsActive BIT
)

DROP TABLE SkatUser


CREATE TABLE SkatYear (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Label TEXT,
    CreatedAt DATETIME,
    ModifiedAt DATETIME,
    StartDate DATETIME,
    EndDate DATETIME
)

DROP TABLE SkatYear

CREATE TABLE SkatUserYear (
    Id INTEGER PRIMARY KEY,
    SkatUserId INTEGER NOT NULL,
    SKatYearId INTEGER NOT NULL,
    UserId TEXT,
    IsPaid BIT,
    Amount INTEGER,
    FOREIGN KEY (SkatUserId) REFERENCES SkatUser(Id),
    FOREIGN KEY (SKatYearId) REFERENCES SkatYear(Id)
)

DROP TABLE SkatUserYear