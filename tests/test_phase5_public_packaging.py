from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def test_phase5_public_packaging_files_exist():
    required = [
        'README.md',
        '.env.example',
        'docs/publication-checklist.md',
        'docs/reproducibility.md',
    ]
    for path in required:
        assert (ROOT / path).exists(), path


def test_readme_is_public_research_kit_not_private_repo():
    text = read('README.md').lower()
    assert 'research kit' in text
    assert 'quick start' in text
    assert 'private research repo' not in text
    assert 'no credentials are committed' in text


def test_public_packaging_docs_keep_phase6_out_of_scope():
    text = read('docs/publication-checklist.md').lower()
    assert 'no live monitor' in text
    assert 'recommendation engine' in text
    assert 'recurring job' in text


def test_public_docs_do_not_reference_local_private_paths():
    checked = [
        'README.md',
        'docs/reproducibility.md',
        'docs/publication-checklist.md',
        'configs/study.oil-hormuz.example.yaml',
        'scripts/collect_all_post_activity_windows.mjs',
        'scripts/run_oil_hormuz_report.py',
        'package.json',
    ]
    forbidden = [
        '/' + 'opt/data/chris',
        '/' + 'opt/hermes',
        '/' + 'root/',
        'HERMES_HOME=' + '/' + 'opt/data/.hermes',
    ]
    for path in checked:
        text = read(path)
        for needle in forbidden:
            assert needle not in text, f'{needle} found in {path}'


def test_public_package_names_chris_lee_as_author():
    assert 'Author: Chris Lee.' in read('README.md')
    assert 'author: Chris Lee' in read('SKILL.md')
    assert '"author": "Chris Lee"' in read('package.json')
    assert 'authors = [{ name = "Chris Lee" }]' in read('pyproject.toml')


def test_public_package_has_no_mit_license_file_or_claim():
    assert not (ROOT / 'LICENSE').exists()
    assert 'MIT. See `LICENSE`.' not in read('README.md')
    assert 'license: MIT' not in read('SKILL.md')
