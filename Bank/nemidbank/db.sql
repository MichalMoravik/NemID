CREATE TABLE [Account](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [BankUserId] INTEGER NOT NULL,
    [AccountNo] TEXT NOT NULL,
    [IsStudent] BOOLEAN NOT NULL CHECK (IsStudent IN (0,1)),
    [CreatedAt] TEXT NOT NULL,
    [ModifiedAt] TEXT NOT NULL,
    [Amount] INTEGER NOT NULL,
    FOREIGN KEY([BankUserId]) REFERENCES [BankUser](Id)
);

CREATE TABLE [BankUser](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [UserId] INTEGER NOT NULL,
    [CreatedAt] TEXT NOT NULL,
    [ModifiedAt] TEXT NOT NULL
);

CREATE TABLE [Loan](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [BankUserId] INTEGER NOT NULL,
    [CreatedAt] TEXT NOT NULL,
    [ModifiedAt] TEXT NOT NULL,
    [Amount] INTEGER NOT NULL,
    FOREIGN KEY([BankUserId]) REFERENCES [BankUser](Id)
);

CREATE TABLE [Deposit](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [BankUserId] INTEGER NOT NULL,
    [CreatedAt] TEXT NOT NULL,
    [Amount] INTEGER NOT NULL,
    FOREIGN KEY([BankUserId]) REFERENCES [BankUser](Id)
);


-- DROP TABLE Account
-- DROP TABLE BankUser
-- DROP TABLE Loan
-- DROP TABLE Deposit