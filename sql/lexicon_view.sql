DROP VIEW IF EXISTS lexicons;
CREATE VIEW lexicons AS
SELECT 
	L.lang_config_id, 
	c.word,
	c.word_ipa,
	c.word_id,
	s.definition,
	s.synset_id,
	s.db_id, 
	s.pos,
	s.lemmas,
	s.examples,
	s.eng_word,
	s.hypernyms,
	s.hyponyms,
	s.holonyms,
	s.meronyms
FROM lang_configs L
CROSS JOIN synsets S
LEFT JOIN conlang_defs D USING (db_id)
LEFT JOIN conlang_words C USING (word_id, lang_config_id)