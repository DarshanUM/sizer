#!/bin/bash

cd sizer/sizer/webapps
echo "Installing bower components(Ignoring if present)"
npm install
bower install --allow-root
#npm install grunt-ng-annotate --save-dev
echo "Building dist"
grunt build --force
#echo "removing bower and node modules"
#rm -rf bower_components node_modules
rm -rf app app-environments test .tmp
cd -
