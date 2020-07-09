import sys
sys.path.insert(0,".")
from modules import get_pdfs
import unittest
import os

class TestGetPDFs(unittest.TestCase):

    def test_cleanhtml(self):
        testString1 = "<span> DECLARATION of Matthew Ambros & William Seymour in ... </span>"
        testString2 = "<span>***NOTE TO ATTORNEY TO RE-FILE DOCUMENT - NON-ECF DOCUMENT ERROR. Note to ... </span>"
        testString3 = "<span>Minute Entry for proceedings held before Judge Katherine Polk Failla: ...</span>"
        testString4 = "MOTION_TO_DECLARE_SECTION_921.1417_FLA_STAT_UNCONSTITUTIONAL_AND_REQUEST_FOR_PROFFER_OF_VICTIM_IMPACT_TESTIMONY_AND_PRETRIAL_RULING_ON_WHETHER_THE_DANGER_OF_UNFAIR_PREJUDICE_OF_THAT_EVIDENCE_OUTWEIGHS_ITS_PROBATIVE_VALUE_ANDOR_OTHERWISE_DENIES_A_FAIR_SENTENCING_PROCEEDING_entered_01222020."
        result1 = get_pdfs.cleanhtml(testString1)
        result2 = get_pdfs.cleanhtml(testString2)
        result3 = get_pdfs.cleanhtml(testString3)
        result4 = get_pdfs.cleanhtml(testString4)
        self.assertEqual(result1, "DECLARATION_of_Matthew_Ambros__William_Seymour_in_")
        self.assertEqual(result2, "NOTE_TO_ATTORNEY_TO_RE-FILE_DOCUMENT_-_NON-ECF_DOCUMENT_ERROR_Note_to_")
        self.assertEqual(result3, "Minute_Entry_for_proceedings_held_before_Judge_Katherine_Polk_Failla_")
        self.assertEqual(result4, "MOTION_TO_DECLARE_SECTION_9211417_FLA_STAT_UNCONSTITUTIONAL_AND_REQUEST_FOR_PROFFER_OF_VICTIM_IMPACT_TESTIMONY_AND_PRETRIAL_RULING_ON_WHETHER_THE_DANGER_OF_UNFAIR_PREJUDICE_OF_THAT_EVIDENCE_OUTWEIGHS_ITS_PROBATIVE_VALUE_ANDOR_OTHERWISE_DENI")

    def test_download_from_link_list(self):
        get_pdfs.download_from_link_list("https://www.nasa.gov/pdf/390539main_Athlete%20Fact%20Sheet.pdf","test_pdf","pdf_test", "test")
        bool_ = os.path.isfile(os.path.join('test',"pdf_test",'test_pdf.pdf'))
        self.assertTrue(bool_)
        os.remove(os.path.join("test","pdf_test", 'test_pdf.pdf'))
        os.rmdir(os.path.join("test","pdf_test"))

    def test_add_path_to_list_of_tuples(self):
        testInput = [("eggs", "milk"), ("onions", "flour"), ("toothpaste", "orange juice")]
        expectedResult = [("eggs", "milk", "sand"), ("onions", "flour","sand"), ("toothpaste", "orange juice", "sand")]
        actualResult = get_pdfs.add_path_to_list_of_tuples(testInput, "sand")
        self.assertEqual(expectedResult,actualResult)

if __name__ == '__main__':
    unittest.main()
