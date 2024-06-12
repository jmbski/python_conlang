from __future__ import annotations
from typing import List
from inspect import isclass, isfunction
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey, 
    String,
    Text,
    JSON,
    Table,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    def to_json(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_') and not isfunction(value) and not isclass(value)}
    
    def __repr__(self) -> str:
        return get_repr(self)
    
def get_repr(entity: Base) -> str:
    """ Function to get the representation of an entity """
    repr_str = f'{entity.__class__.__name__}('
    for key, value in entity.__dict__.items():
        if(key.startswith('_') or isfunction(value) or isclass(value)):
            continue
        repr_str += f'{key}={value!r}, '
    repr_str = repr_str[:-2] + ')'
    return repr_str

conlang_defs = Table(
    "conlang_defs",    Base.metadata,
    Column('db_id', BigInteger, ForeignKey("synsets.db_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    Column('word_id', BigInteger, ForeignKey("conlang_words.word_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    PrimaryKeyConstraint('db_id', 'word_id')
)

synset_relations = Table(
    "synset_relations",    Base.metadata,
    Column('db_id_1', BigInteger, ForeignKey("synsets.db_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    Column('db_id_2', BigInteger, ForeignKey("synsets.db_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    Column('relation_type', String(255), nullable=False),
    PrimaryKeyConstraint('db_id_1', 'db_id_2', 'relation_type'),
)

class LangConfig(Base):
    __tablename__ = "lang_configs"
    lang_config_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phonetic_inventory: Mapped[dict] = mapped_column(JSON, nullable=False)
    orthography_categories: Mapped[dict] = mapped_column(JSON, nullable=False)
    orth_syllables: Mapped[dict] = mapped_column(JSON, nullable=False)
    grapheme_lookup: Mapped[dict] = mapped_column(JSON, nullable=False)
    debug: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    conlang_words: Mapped[List['ConlangWord']] = relationship(back_populates='lang_config')
    
class ConlangWord(Base):
    __tablename__ = "conlang_words"
    word_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    word_ipa: Mapped[str] = mapped_column(String(255), nullable=False)
    lang_config_id: Mapped[int] = mapped_column(ForeignKey("lang_configs.lang_config_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    
    lang_config: Mapped['LangConfig'] = relationship(back_populates='conlang_words')
    synsets: Mapped[List[Synset]] = relationship(secondary=conlang_defs, back_populates='conlang_words')
    
class Synset(Base):
    __tablename__ = "synsets"
    db_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    synset_id: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    pos: Mapped[str] = mapped_column(String(255), nullable=False)
    examples: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    lemmas: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    eng_word: Mapped[str] = mapped_column(String(255), nullable=False)
    hypernyms: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    hyponyms: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    holonyms: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    meronyms: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    
    conlang_words: Mapped[List[ConlangWord]] = relationship(secondary=conlang_defs, back_populates='synsets')
    
class Lexicon(Base):
    __tablename__ = 'lexicons'
    lang_config_id: Mapped[int] = mapped_column()
    word: Mapped[str] = mapped_column(String(255))
    word_ipa: Mapped[str] = mapped_column(String(255))
    word_id: Mapped[int] = mapped_column()
    definition: Mapped[str] = mapped_column(Text)
    synset_id: Mapped[str] = mapped_column(String(255))
    db_id: Mapped[int] = mapped_column()
    pos: Mapped[str] = mapped_column(String(255))
    lemmas: Mapped[List[str]] = mapped_column(JSON)
    examples: Mapped[List[str]] = mapped_column(JSON)
    eng_word: Mapped[str] = mapped_column(String(255))
    hypernyms: Mapped[List[str]] = mapped_column(JSON)
    hyponyms: Mapped[List[str]] = mapped_column(JSON)
    meronyms: Mapped[List[str]] = mapped_column(JSON)
    holonyms: Mapped[List[str]] = mapped_column(JSON)

    __table_args__ = (
        PrimaryKeyConstraint('lang_config_id', 'word_id', 'db_id'),
    )