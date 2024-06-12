from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy import insert, update

from data_builder.entities import Synset, ConlangWord, LangConfig, conlang_defs, Lexicon
from data_builder import lang_tools

from warskald import AttrDict, utils

import os

DB_PATH = os.environ.get('CONLANG_DB_PATH', '/home/joseph/coding_base/silverlight/conlang/python/langs_data.sqlite3')
""" Path to the SQLite3 database file """

DB_URI = f'sqlite:///{DB_PATH}'
""" URI for the SQLite3 database """

engine = create_engine(DB_URI)

session = scoped_session(sessionmaker(bind=engine))


# Create a configured "Session" class
session_factory = sessionmaker(bind=engine)

# Create a scoped session
DBSession = scoped_session(session_factory)

def init_db():
    """ Function to initialize the database (create tables) """
    from .entities import Base  # Import your Base class from entities
    Base.metadata.create_all(bind=engine)

def get_session():
    """ Function to get a new session """
    return DBSession()

def close_session(db_session: Session, commit: bool = False):
    """ Function to close a session """
    if(commit):
        db_session.commit()
    db_session.close()
    
def shutdown_session(exception=None):
    """ Make sure to close the session after usage """
    DBSession.remove()
    
def get_all_synsets():
    """ Function to get all synsets from the database """
    
    db_session = get_session() #g.db_session

    synsets = db_session.query(Synset).all()

    # Example of serializing synsets to JSON

    synsets_list = [
        {
            "db_id": synset.db_id,
            "synset_id": synset.synset_id,
            "definition": synset.definition,
            "pos": synset.pos,
            "examples": synset.examples,
            "lemmas": synset.lemmas,
            "eng_word": synset.eng_word
        }
        for synset in synsets
    ]

    return synsets_list

def get_conlang_word(conlang_word: AttrDict, session: Session = None):
    """ Function to get a conlang word from the database """
    
    db_session = session if session else get_session()
    print(f'word: {conlang_word.word} lang_id: {conlang_word.lang_config_id}')
    conlang_word = db_session.scalars(
        select(ConlangWord)
        .where(ConlangWord.word_id == conlang_word.word_id if conlang_word.word_id \
            else ConlangWord.word == conlang_word.word)
        .where(ConlangWord.lang_config_id == conlang_word.lang_config_id)
    ).first()
    
    if(not session):
        db_session.close()
    
    return conlang_word
    
def get_lang_words(lang_id: int, session: Session = None):
    """ Function to get all conlang words for a language """
    
    db_session = session if session else get_session()
    
    conlang_words = db_session.query(ConlangWord).filter(ConlangWord.lang_config_id == lang_id).all()
    
    return conlang_words

def save_conlang_word(conlang_word: AttrDict, session: Session = None):
    """ Function to save a conlang word to the database """
    
    
    db_session = session if session else get_session()
   
    if(get_conlang_word(conlang_word, db_session)):
       
        db_word = db_session.scalars(
            update(ConlangWord)
            .where(ConlangWord.word_id == conlang_word.word_id)
            .values(conlang_word)
            .returning(ConlangWord)
        ).first()
    else:
        db_word = db_session.scalars(
            insert(ConlangWord).returning(ConlangWord),
            [conlang_word]
        ).first()
    
    if(not session):
        db_session.commit()
    
    return db_word
    
def delete_conlang_word(word: str, session: Session = None):
    """ Function to delete a conlang word from the database """
    
    db_session = session if session else get_session()
    
    db_conlang_word = get_conlang_word(word, db_session)
    
    if(db_conlang_word):
        db_session.delete(db_conlang_word)
        
    if(not session):
        db_session.commit()
        print(f'Conlang word {db_conlang_word.word} deleted')

def get_synset(synset_id: str | int, db_session: Session = None):
    """ Function to get a synset from the database """
    if(db_session is None):
        db_session = get_session()
        
    synset = db_session.query(Synset)\
        .filter(Synset.synset_id == synset_id if isinstance(synset_id, str)\
        else Synset.db_id == synset_id).first()
    
    return synset

def get_synsets(session: Session = None):
    """ Function to get all synsets from the database """
    
    db_session = session if session else get_session()
    
    synsets = db_session.query(Synset).all()
    
    return synsets
    
def delete_synset(synset_id: str, sesion=None):
    """ Function to delete a synset from the database """
    
    db_session = session if session else get_session()
    
    db_synset = get_synset(synset_id, db_session)
    
    if(db_synset):
        db_session.delete(db_synset)
    if(not session):
        db_session.commit()
        print(f'Synset for {db_synset.eng_word}:{db_synset.synset_id} deleted')
        
def get_conlang_def(synset_db_id: int, conlang_word_id: int, session: Session = None):
    """ Function to get a conlang definition from the database """
    
    db_session = session if session else get_session()
    
    conlang_def = db_session.query(conlang_defs)\
        .filter(conlang_defs.c.db_id == synset_db_id)\
        .filter(conlang_defs.c.word_id == conlang_word_id).first()
    
    return conlang_def
        
def associate_conlang_synset(
    conlang_word: ConlangWord | str | int,
    synset: Synset | str, 
    lang_id: int = 1,
    session: Session = None):
    """ Function to associate a conlang word with a synset """
    
    db_session = session if session else get_session()
    
    if(not isinstance(conlang_word, ConlangWord)):
        conlang_word = get_conlang_word(conlang_word, lang_id, db_session)
    if(not isinstance(synset, Synset)):
        synset = get_synset(synset, db_session)
    
    
    if(conlang_word and synset):
        link_ref = get_conlang_def(synset.db_id, conlang_word.word_id, db_session)
        if(link_ref):
            pass
        else:
            db_session.execute(
                insert(conlang_defs).values(
                    db_id=synset.db_id,
                    word_id=conlang_word.word_id
                )
            )
        
    if(not session):
        db_session.commit()
        
def save_synset(synset: AttrDict, session: Session = None):
    """ Function to save a synset to the database """
    
    db_session = session if session else get_session()
    
    db_synset = get_synset(synset.synset_id, db_session)
    
    updated = False
    
    if(db_synset):
        # if it already exists, update the value in the database
        db_synset = db_session.scalars(
            update(Synset)
            .where(Synset.synset_id == synset.synset_id)
            .values(synset)
            .returning(Synset)
        )
        
        updated = True
        
    else:
        #utils.pretty_print(synset)
        if(not synset.get('db_id')):
            synset.pop('db_id', None)
        db_synset = db_session.scalars(
            insert(Synset).returning(Synset),
            [synset]
        )
    db_synset = db_synset.first()
    
    
    if(not session):
        action_str = 'updated' if updated else 'saved'
        print(f'Synset for {db_synset.eng_word}:{db_synset.synset_id} {action_str} with db_id: {db_synset.db_id}')
        db_session.commit()
    return db_synset

def get_lang_configs():
    """ Function to get the language configurations from the database """
    
    db_session = get_session()
    
    lang_configs = db_session.query(LangConfig).all()
    
    return [ lang_config.to_json() for lang_config in lang_configs ]

def get_lang_config(lang_config_id: int, session: Session) -> dict | None:
    """ Function to get a language configuration from the database """
    
    db_session = session if session else get_session()
    
    lang_config = db_session.query(LangConfig).filter(LangConfig.lang_config_id == lang_config_id).first()
    
    if(not session):
        db_session.close()
    return lang_config

def save_lang_config(lang_config: dict, session: Session = None):
    """ Function to save a language configuration to the database """
    
    db_session = session if session else get_session()
    
    db_lang_config = get_lang_config(lang_config['lang_config_id'], db_session)
    
    updated = False
    
    if(db_lang_config):
        # if it already exists, update the value in the database
        print('updating lang_config:', lang_config['lang_config_id'])
        db_lang_config = db_session.scalars(
            update(LangConfig)
            .where(LangConfig.lang_config_id == lang_config['lang_config_id'])
            .values(lang_config)
            .returning(LangConfig),
        )
        
        updated = True
        
    else:
        #utils.pretty_print(synset)
        lang_config.pop('lang_config_id', None)
        db_lang_config = db_session.scalars(
            insert(LangConfig).returning(LangConfig),
            [lang_config]
        )
    if(not session):
        action_str = 'updated' if updated else 'saved'
        print(f'Synset for {db_lang_config.eng_word}:{db_lang_config.synset_id} {action_str} with db_id: {db_lang_config.db_id}')
        db_session.commit()
    return db_lang_config

def get_lexicon(lang_id: int, session: Session = None):
    """ Function to get the lexicon for a language """
    
    db_session = session if session else get_session()
    
    lexicon = db_session.query(Lexicon).filter(Lexicon.lang_config_id == lang_id).all()
    
    if(not session):
        db_session.close()
    
    return lexicon