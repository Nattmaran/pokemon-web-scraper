import unittest
import scraper

class ReadPokemonData(unittest.TestCase):
    def setUp(self):
        self.filename = 'test-hitmontop.html'
        self.html_data = open(self.filename,'r')

    def test_get_pokemon_data(self):
        pokemon = scraper.get_pokemon_data(self.html_data)
        self.assertEqual(pokemon['name'],'Hitmontop','Wrong pokemon name')

    def tearDown(self):
        self.html_data.close()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ReadPokemonData('testing reading from a serebii.net pokemon site'))
    return suite;

if __name__ == '__main__':
    unittest.main()
