CREATE TABLE User(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Email TEXT NOT NULL,
    NemId TEXT NOT NULL,
    CPR TEXT NOT NULL,
    CreatedAt TEXT NOT NULL,
    ModifiedAt TEXT NOT NULL,
    GenderId INTEGER NOT NULL,
    FOREIGN KEY(GenderId) REFERENCES Gender(Id)
);

CREATE TABLE Password(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    CreatedAt TEXT NOT NULL,
    PasswordHash TEXT NOT NULL,
    IsValid BOOLEAN NOT NULL CHECK (IsValid IN (0,1)),
    UserId INTEGER NOT NULL,
    FOREIGN KEY(UserId) REFERENCES User(Id) ON DELETE CASCADE
);

CREATE TABLE Gender(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Label TEXT NOT NULL
);

-- INSERT INTO Gender(Label) VALUES ('male');
-- INSERT INTO Gender(Label) VALUES ('female');
-- INSERT INTO Gender(Label) VALUES ('transgender');


-- INSERT INTO User(Email, NemId, CPR, CreatedAt, ModifiedAt, GenderId) VALUES ('Michal', '64434-2211', '2604982211', 'October 31, 2020 01:11AM', 'October 31, 2020 01:11AM', 1)
-- DROP TABLE Gender
-- DROP TABLE Password
-- DROP TABLE User