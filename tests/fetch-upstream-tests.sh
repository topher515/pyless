repogit="https://github.com/cloudhead/less.js"


repodir=".lessjs-master";

# Clone repo if it doesnt exist
if [ ! -d "$repodir" ]
then
  git clone $repogit $repodir
fi

# Fetch and merge latest changes
pushd "$repodir";
git fetch origin;
git merge origin/master;

# Extract tests
git checkout-index -q --prefix="../upstream/" -- test/css/* test/less/* test/less/{errors,import,*}/*;
popd;