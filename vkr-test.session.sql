-- INSERT INTO authors(id, last_name, first_name, middle_name)
-- VALUES 
--   ('90972e67-1b87-4aa1-81ad-4af78951aedd', 'Иванов', 'Пётр', 'Сергеевич'),
--   ('42e58dad-d334-4319-99f7-f10962dfa5e0', 'Семенов', 'Лох', 'Иванович');

INSERT INTO document_authors(document_id, author_id)
VALUES
  ('90972e67-1b87-4aa1-81ad-4af78951aedd', '90972e67-1b87-4aa1-81ad-4af78951aedd'),
  ('90972e67-1b87-4aa1-81ad-4af78951aedd', '42e58dad-d334-4319-99f7-f10962dfa5e0'),
  ('42e58dad-d334-4319-99f7-f10962dfa5e0', '42e58dad-d334-4319-99f7-f10962dfa5e0')