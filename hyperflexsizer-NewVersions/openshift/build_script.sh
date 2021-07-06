#!/bin/bash

while [ : ]

Home="/users/aaybhard/"
Hypersizer="/users/aaybhard/hyperflexsizer"
HYPERFLEX="/users/aaybhard/hyperflexsizer/aqfuiu3xpsn1"
WSGI="/users/aaybhard/hyperflexsizer/aqfuiu3xpsn1/wsgi/"
Hfsizertar="/users/aaybhard/hyperflexwar/"
Temp="/users/aaybhard/bitbucket/"
Comment="added latest tar file $DATE"

do
cd $Home

if  [ ! -d hyperflexwar ];then
   echo "making clone of tar file from bitbucket"
   git clone --depth=1 https://mapleguest-new:mapleguest@bitbucket.org/maplelabsadmin/hyperflexwar.git
   echo "successfully cloned tar file from bitbucket"
   cd $Hfsizertar
   InitialID=$(git log --format="%H" -n 1)
   echo "$InitialID" > /users/aaybhard/deploy/InitialID.txt

else
   echo "Found repo, ************"
   cd $Hfsizertar
   git pull
   NewID=$(git log --format="%H" -n 1)
   cd /users/aaybhard/deploy
   echo "$NewID" > /users/aaybhard/deploy/NewID.txt

   InitialID1=$(head -n 1 /users/aaybhard/deploy/InitialID.txt)
   NewID1=$(head -n 1 /users/aaybhard/deploy/NewID.txt)



   if [ $InitialID1 == $NewID1 ];then
      echo " no changes found"

   else
      echo "Found changes in the remote "

      echo "last commit id"
      echo "$InitialID1"

      echo "new Commit id"
      echo "$NewID1"


      cd $Hfsizertar
      mv -f hyperflexsizer.tar.gz $Temp

      echo "remove bitbucket clone"
      cd $Home
      rm -rf hyperflexwar


      echo "making clone of  lae hyper flex sizer"
      cd $Hypersizer
      git clone ssh://saleemdjangotest-aqfuiu3xpsn1-1@aqfuiu3xpsn1-saleemdjangotest.cloudapps.cisco.com/~/git/aqfuiu3xpsn1.git/
      cd $WSGI
      rm hyperflexsizer.tar.gz
      echo "Removed old tar file"

      echo "moving hyperflexsizer.tar.gz file from temp directory to webapps directory"
      cd $Temp
      mv -f hyperflexsizer.tar.gz $WSGI

      cd $HYPERFLEX

      echo " performing Commit and Push"
      git commit -am"$ added latest tar file, $NewID1"
      git push

      cd $Hypersizer
      rm -rf aqfuiu3xpsn1
      cd $Home
      git clone --depth=1 https://mapleguest-new:mapleguest@bitbucket.org/maplelabsadmin/hyperflexwar.git
      echo "$NewID1" > /users/aaybhard/deploy/InitialID.txt
   fi


fi
sleep 10s
done
