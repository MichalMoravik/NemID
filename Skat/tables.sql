CREATE TABLE SkatUser (
    Id INTEGER PRIMARY KEY,
    UserId TEXT,
    CreatedAt DATETIME,
    IsActive BIT
)

CREATE TABLE SkatYear (
    Id INTEGER PRIMARY KEY,
    Label TEXT,
    CreatedAt DATETIME,
    ModifiedAt DATETIME,
    StartDate DATETIME,
    EndDate DATETIME
)

CREATE TABLE SkatUserYear (
    Id INTEGER PRIMARY KEY,
    SkatUserId INTEGER NOT NULL,
    SKatYearId INTEGER NOT NULL,
    UserId TEXT,
    IsPaid BIT,
    Amount INTEGER,
    FOREIGN KEY (SkatUserId) REFERENCES SkatUser(Id),
    FOREIGN KEY (SKatYearId) REFERENCES SKatYear(Id)
)