import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.disease_knowledge_base import DiseaseKnowledgeBase


def test_kb_init():
    kb = DiseaseKnowledgeBase()
    assert kb is not None


def test_get_all_diseases():
    kb = DiseaseKnowledgeBase()
    diseases = kb.get_all_diseases()
    assert len(diseases) > 0


def test_get_disease_info():
    kb = DiseaseKnowledgeBase()
    info = kb.get_disease_info("Tomato Bacterial Spot")
    assert info is not None
    assert "description" in info
    assert "symptoms" in info
    assert "causes" in info
    assert "prevention" in info
    assert "treatment" in info


def test_get_disease_info_nonexistent():
    kb = DiseaseKnowledgeBase()
    info = kb.get_disease_info("NonExistent Disease")
    assert info is not None
    assert "description" in info


def test_filter_by_crop():
    kb = DiseaseKnowledgeBase()
    diseases = kb.filter_by_crop("Tomato")
    assert len(diseases) > 0
    has_tomato = any("Tomato" in d for d in diseases)
    assert has_tomato


def test_search():
    kb = DiseaseKnowledgeBase()
    results = kb.search("blight")
    assert len(results) > 0


def test_search_no_results():
    kb = DiseaseKnowledgeBase()
    results = kb.search("xyzzyxyz")
    assert isinstance(results, list)


if __name__ == "__main__":
    test_kb_init()
    test_get_all_diseases()
    test_get_disease_info()
    test_get_disease_info_nonexistent()
    test_filter_by_crop()
    test_search()
    test_search_no_results()
    print("All knowledge base tests passed!")
