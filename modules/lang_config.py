from modules import utils
from random import random, choices

class LanguageConfig:
    """ A class representing the various data points for a conlang. """
    
    ipa_escape: dict = {
        '1': 'i',
        'ᵻ': 'ɨ', 
        'ɚ': 'ɹ'
    }
    """ Mapping of IPA characters to their escape characters. This is based on the IPA 
        characters used by phonemizer. 
    """
    
    def __init__(self, init: dict = None) -> None:
        """ Initialize the language data. """
        self.lang_config_id: int = None
        """ The ID of the language. """
        
        self.name: str = ''
        """ Name of the language. """
        
        self.phonetic_inventory: dict = {}
        """ A dictionary whose keys are graphemes and values are IPA phonemes. """
        
        self.orthography_categories: dict = {}
        """ A dictionary whose keys are category IDs and values are lists of graphemes. 
            This is based on the word generators used by many conlang tools that use
            individual capital letters to represent categories of graphemes, but allowing 
            for more flexibility because you can use any valid dictionary key type. 
            Such as a string, tuple, or number.
        """
        
        self.orth_syllables: dict = {}
        """ A dictionary whose keys are combinations of orthographic IDs and values are the syllable weight. 
            A higher syllable weight means the syllable is more likely to appear in the language. These are
            used to generate syllables for the language.
            
            Valid key types for generating syllables are strings or tuples.
        """
        
        self.grapheme_lookup: dict = {}
        """ A dictionary whose keys are IPA phonemes and values are matching graphemes. 
            Effectively the reverse of phonetic_inventory, but allowing you to make custom
            changes if desired. Will be generated automatically if not provided. 
        """
        
        self.debug: bool = False
        """ A flag indicating whether to print debug information. """
        
        if(isinstance(init, dict)):
            for key, value in init.items():
                setattr(self, key, value)
                
            if(self.grapheme_lookup.keys() == []):
                self._generate_grapheme_lookup()
    
    def _generate_grapheme_lookup(self) -> None:
        """ Generate the grapheme lookup dictionary. """
        
        for key, value in self.phonetic_inventory.items():
            self.grapheme_lookup[value] = key
            
    def generate_syllable(self, category: str | tuple) -> list[str]:
        syllable = []
        
        for letter in category:
            if(isinstance(letter, (str, tuple)) == False):
                raise ValueError(f'Invalid category type for {self.name}.orthography_categories.{category}.{letter}, {type(letter)}. Must be a string or tuple.')
            
            
            phonemes = self.orthography_categories.get(letter)
            if(self.debug):
                utils.debug_print('phonemes', phonemes)
                
            if(phonemes):
                index = int(random() * len(phonemes))
                
                phoneme = phonemes[index]
                
                if(self.debug):
                    utils.debug_print(f'phonemes length: {len(phonemes)}, index: {index}, phoneme: {phoneme}')
                    
                ipa = self.phonetic_inventory.get(phoneme)
                
                if(not ipa and self.debug):
                    utils.debug_print(f"phoneme '{phoneme}' not found in {self.name}.phonetic_inventory")
                else:
                    syllable.append(phoneme)
        
        if(self.debug):
            utils.debug_print(f'{self.name} syllable - {syllable}')
            
        return syllable

    def get_category_group(self):
        """ Get a category group for generating a syllable based on the orthographic syllable weights.

        Returns:
            str | tuple: The category group for generating a syllable.
        """
                
        keys = list(self.orth_syllables.keys())
        weights = list(self.orth_syllables.values())
        
        return choices(keys, weights)[0]

    def to_graphemes(self, chars: list[str]):
        """ Convert a list of IPA phonemes to graphemes.

        Args:
            chars (list[str]): A list of IPA phonemes.

        Returns:
            str: The grapheme representation of the IPA phonemes.
            
        """
                
        grapheme_word = ''
        
        for char in chars:
            grapheme = self.grapheme_lookup.get(char)
            if(not grapheme):
                if(self.debug):
                    utils.debug_print(f"{self.name}.to_graphemes: char '{char}', grapheme_word: '{grapheme_word}', chars: {chars}, not found")
                continue
            grapheme_word += self.grapheme_lookup.get(char)
        
        if(self.debug):
            utils.debug_print(f'{self.name}.to_graphemes: {grapheme_word}')
        return grapheme_word

    def to_ipa(self, chars: list[str]):
        """ Convert a list of graphemes to IPA phonemes.

        Args:
            chars (list[str]): A list of graphemes.

        Returns:
            str: The IPA phoneme representation of the graphemes.
        """
                
        ipa_word = ''
        for char in chars:
            ipa_char = self.phonetic_inventory.get(char)
            if(not ipa_char):
                if(self.debug):
                    utils.debug_print(f"{self.name}.to_ipa: char '{char}', ipa_word: '{ipa_word}', chars: {chars}, not found")
                continue
            ipa_word += ipa_char
            
        if(self.debug):
            utils.debug_print(f'{self.name}.to_ipa: {ipa_word}')
            
        return ipa_word
        
    def generate_word(self, syllables: int = None, minimum: int = 1, maximum: int = 3):
        """ Generate a word based on the language data properties of this class.

        Args:
            syllables (int, optional): Set a specific amount of syllables to use, 
                if None, will use a random value between min and max. Defaults to None.
            minimum (int, optional): minimum number of syllables. Defaults to 1.
            maximum (int, optional): maximum number of syllables. Defaults to 3.

        Returns:
            tuple[str]: randomly generated word, first value is using graphemes, second value is using IPA phonemes.
        """
        
        if(syllables):
            count = syllables
        else:
            count = int(random() * (maximum - minimum + 1)) + minimum
        
        word_chars = []
        
        for _ in range(count):
            category = self.get_category_group()
            
            word_chars.extend(self.generate_syllable(category))
            
        if(self.debug):
            utils.debug_print(f'{self.name}.{self.generate_word.__name__}: word_chars - {word_chars}')
            
        word = ''.join(word_chars)
        word_ipa = self.to_ipa(word_chars)
            
        if(self.debug):
            utils.debug_print(f'{self.name}.{self.generate_word.__name__}: graphemes: {word}, IPA: {word_ipa}')
            
        return word, word_ipa
    
    def generate_words(self, count: int = 100, syllables: int = None, minimum: int = 1, maximum: int = 3) -> list[tuple[str]]:
        """ Generate a list of words based on the language data properties of this class.

        Args:
            count (int, optional): Number of words to generate. Defaults to 100.
            syllables (int, optional): Set a specific amount of syllables to use, 
                if None, will use a random value between min and max. Defaults to None.
            minimum (int, optional): minimum number of syllables. Defaults to 1.
            maximum (int, optional): maximum number of syllables. Defaults to 3.

        Returns:
            list[tuple[str]]: A list of randomly generated words, each tuple contains two values, 
                the first value is using graphemes, the second value is using IPA phonemes.
        """
                
        words: list[tuple[str]] = []
        
        for _ in range(count):
            words.append(self.generate_word(syllables, minimum, maximum))
            
        return words