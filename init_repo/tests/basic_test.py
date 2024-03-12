import unittest
from unittest.mock import MagicMock, patch
from init_repo import download_manifest
class TestDownloadManifest(unittest.TestCase):
    @patch('git.Repo.clone_from')
    @patch('builtins.open', create=True)
    @patch('git.Repo.create_submodule')
    @patch('urllib.parse.urlparse')
    @patch('urllib.parse.urlopen')
    
    def test_download_manifest(self, mock_create_submodule, mock_open, mock_clone_from):
        mock_repo = MagicMock()
        mock_repo.working_dir = '/path/to/repo'
        mock_clone_from.return_value = mock_repo
        mock_open.return_value.read.return_value = '<manifest><projects><remote name="test" fetch="that.url"\><project remote="test" name="name" revision="revision"/></projects></manifest>'

        manifest_data = download_manifest("https://github.com/example/repo.git", "manifest.xml")

        self.assertEqual(manifest_data, {'manifest': {'remote':{'@name':'test', '@fetch':'that.url'},'projects': {'project': {'@remote': 'test', '@name': 'name', '@revision': 'revision'}}}})
        mock_create_submodule.assert_called_once_with('name', 'url', branch='revision')
