git pull cn master

for fname in `find ./content/ -name *.md -or -name *.markdown`
do
  scripts/add-readmore.py ${fname}
done

if [ "`git status content | grep modified`" != "" ]; then
  echo "update content"
  git add ./content
  git commit -m "add more tag"
  git push cn master
  git push origin master
fi

hugo -D -v
sh Hazy2019.github.io/scripts/publish.sh
