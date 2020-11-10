CREATE TABLE [Token](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [AuthAttemptId] INTEGER NOT NULL,
    [Token] TEXT NOT NULL,
    [CreatedAt] TEXT NOT NULL,
    FOREIGN KEY ([AuthAttemptId]) REFERENCES [AuthAttempt](Id)
);

CREATE TABLE [AuthAttempt](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [NemId] TEXT NOT NULL,
    [GeneratedCode] TEXT NOT NULL,
    [CreatedAt] TEXT NOT NULL,
    [StateId] INTEGER NOT NULL,
    FOREIGN KEY ([StateId]) REFERENCES [State](Id)
);

CREATE TABLE [State](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Label] TEXT NOT NULL
);

-- DROP TABLE State;
-- DROP TABLE AuthAttempt;
-- DROP TABLE Token;