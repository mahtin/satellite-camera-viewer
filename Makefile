#
# Copyright (C) 2023-2026 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
#

PYTHON = python
PIP = pip
PYLINT = pylint
TWINE = twine
TWINE = ${PYTHON} -m twine
BUILD = ${PYTHON} -m build -C--quiet

NAME = "satellite-camera-viewer"
NAME_ = "satellite_camera_viewer"

SOURCE = src/SatelliteCameraViewer

all: CHANGELOG.md
	${FORCE}

CHANGELOG.md: FORCE
	@tmp=/tmp/_$$$$.md ; \
	( \
		cp /dev/null $$tmp ; \
		echo '# Change Log' ; \
		echo '' ; \
		git log --date=iso-local --pretty=format:' - %ci [%h](../../commit/%H) %s' ; \
		echo '' ; \
	)  >> $$tmp ; \
	diff $$tmp CHANGELOG.md || ( cp $$tmp CHANGELOG.md ; echo "CHANGELOG.md - updated" ) ; \
	rm $$tmp
FORCE:

lint:
	${PYLINT} --unsafe-load-any-extension=y ${SOURCE}

clean:
	rm -rf build dist
	mkdir build dist
	rm -rf src/${NAME_}.egg-info

test: all
	${FORCE}

sdist: all
	# make clean
	# make test
	# $(TWINE)
	$(BUILD)
	@ v=`ls -t dist/${NAME_}-*-py3-none-any.whl | head -1` ; echo $(TWINE) check $$v ; $(TWINE) check $$v
	@ rm -rf src/${NAME_}.egg-info build

bdist: all
	${PIP} wheel . -w dist --no-deps
	@ v=`ls -t dist/${NAME_}-*-py3-none-any.whl | head -1` ; echo $(TWINE) check $$v ; $(TWINE) check $$v
	@ rm -rf src/${NAME_}.egg-info build

showtag: sdist
	@ v=`ls -t dist/${NAME_}-*-py3-none-any.whl | head -1 | sed -e "s/dist\/${NAME_}-//" -e 's/-py3-none-any.whl//'` ; echo "\tDIST VERSION =" $$v ; (git tag | fgrep -q "$$v") && echo "\tGIT TAG EXISTS"

tag: sdist
	@ v=`ls -t dist/${NAME_}-*-py3-none-any.whl | head -1 | sed -e "s/dist\/${NAME_}-//" -e 's/-py3-none-any.whl//'` ; echo "\tDIST VERSION =" $$v ; (git tag | fgrep -q "$$v") || git tag "$$v"

upload: clean all tag upload-github upload-pypi

upload-github:
	git push
	git push origin --tags

upload-pypi: sdist bdist
	@ v=`ls -t dist/${NAME_}-*-py3-none-any.whl | head -1` ; echo $(TWINE) check $$v ; $(TWINE) check $$v
	${TWINE} upload --repository ${NAME} `ls -t dist/${NAME_}-*-py3-none-any.whl|head -1`

HTML = singlehtml
HTML = html

MULTIPROCESSING = -j auto
MULTIPROCESSING = -j 1

docs: all
	sphinx-apidoc -Mfe -o docs ${SOURCE}
	sphinx-build ${MULTIPROCESSING} -b ${HTML} docs docs/_build/html

clean-docs: all
	rm -rf docs/*.rst docs/_build/

