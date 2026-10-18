"""Publication faults must preserve the prior complete local generation."""
import json
import pytest
from arena.reports import refresh_release as release
from arena.evaluation import freeze


def test_release_loader_is_idempotent():
    html='''<script src="js/data/season_01.js?v=old"></script>
<script src="js/data/arena_release.js?v=old"></script>
<script src="js/data/arena_release.js?v=old"></script>
<script src="js/adapter.js?v=old"></script>
'''
    result=release.release_html(html,'generation_a')
    assert result.count('src="js/data/')==1
    assert 'season_01.js' not in result
    assert release.release_html(result,'generation_a')==result
    assert 'v=generation_b' in release.release_html(result,'generation_b')


def test_frozen_inputs_survive_catalog_reordering(tmp_path):
    path=tmp_path/'inputs';path.mkdir()
    frozen=path/'fixture.txt';frozen.write_text('unchanged frozen input')
    release.save_json(path/'manifest.json',dict(cutoff='2026-10-09',
        seasons=['season_01','season_csi1000','season_csi300','season_csi500','season_csi800'],
        files={'inputs/fixture.txt':release.digest(frozen)}))
    reordered=['season_01','season_csi300','season_csi500','season_csi800','season_csi1000']
    result=freeze(tmp_path,reordered,'2026-10-09')
    assert result['files']['inputs/fixture.txt']==release.digest(frozen)
    with pytest.raises(ValueError,match='selection differs'):
        freeze(tmp_path,reordered[:-1],'2026-10-09')


@pytest.mark.parametrize('private_journal',[False,True])
@pytest.mark.parametrize('interruption',['before_swap','after_backup','after_install'])
def test_interrupted_publication_recovery(tmp_path,monkeypatch,interruption,private_journal):
    monkeypatch.setattr(release,'REPO_ROOT',tmp_path)
    monkeypatch.setattr(release,'RUNS_DIR',tmp_path/'runs')
    root=tmp_path/'artifacts/evaluations/generation_a'
    target=tmp_path/'runs/season_01_run';target.mkdir(parents=True)
    (target/'generation.txt').write_text('old')
    staged=root/'staging/runs/season_01_run';staged.mkdir(parents=True)
    (staged/'generation.txt').write_text('new')
    public=tmp_path/'web/index.html';public.parent.mkdir();public.write_text('new html')
    backup=root/'publication_backup/web/index.html';backup.parent.mkdir(parents=True)
    backup.write_text('old html')
    new_file=tmp_path/'web/new.md';new_file.write_text('new report')
    cache=tmp_path/'artifacts/predictions/synthetic.pkl';cache.parent.mkdir(parents=True)
    cache.write_bytes(b'new anonymous scores')
    cache_backup=root/'publication_backup/artifacts/predictions/synthetic.pkl';cache_backup.parent.mkdir(parents=True)
    cache_backup.write_bytes(b'old anonymous scores')
    registry=tmp_path/'manifests/private/alias_map.yaml';registry.parent.mkdir(parents=True)
    registry.write_text('new anonymous registration')
    item=dict(name=target.name,ready='.season_01_generation_a.ready',existed=True)
    journal=dict(phase='prepared',runs=[item],files=[
        dict(path='web/index.html',existed=True),dict(path='web/new.md',existed=False),
        dict(path='artifacts/predictions/synthetic.pkl',existed=True),dict(path='manifests/private/alias_map.yaml',existed=False)])
    journal_path=root/('private/publication_journal.json' if private_journal else 'publication_journal.json')
    release.save_json(journal_path,journal)
    if interruption=='after_backup':
        replace=release.os.replace
        def fail_install(source,destination):
            if str(source).endswith('.ready'):raise OSError('simulated install failure')
            return replace(source,destination)
        monkeypatch.setattr(release.os,'replace',fail_install)
        with pytest.raises(OSError,match='simulated install failure'):
            release.replace_run(root,item)
        monkeypatch.setattr(release.os,'replace',replace)
        assert not target.exists()
    elif interruption=='after_install':
        release.replace_run(root,item)
        assert (target/'generation.txt').read_text()=='new'
    release.recover_pending_publications()
    assert (target/'generation.txt').read_text()=='old'
    assert public.read_text()=='old html'
    assert not new_file.exists()
    assert cache.read_bytes()==b'old anonymous scores'
    assert not registry.exists()
    assert not (tmp_path/'runs'/item['ready']).exists()
    assert json.loads(journal_path.read_text())['phase']=='rolled_back'
    assert not release.recover_publication(root)
