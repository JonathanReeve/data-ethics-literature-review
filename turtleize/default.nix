# with import <nixpkgs> {};

with import (builtins.fetchGit {
  # Descriptive name to make the store path easier to identify
  # name = "nixos-unstable-2021-05-17";
  url = "https://github.com/nixos/nixpkgs/";
  # Commit hash for nixos-unstable as of 2021-05-17
  # `git ls-remote https://github.com/nixos/nixpkgs nixos-unstable`
  # ref = "refs/heads/nixos-unstable";
  allRefs = true;
  # rev = "83d907fd760d9ee4f49b4b7e4b1c6682f137b573";
  rev = "19b22191f7de3d172562f2fdcf1e9be21df23fef";
}) {};

( let
    customPython = pkgs.python38.buildEnv.override rec {
      extraLibs = with pkgs.python38Packages; [
        # pkgs.chromedriver
        matplotlib
        pandas
        jupyter
        scikitlearn
        # newAltair
        dominate
        # plotly
        # newPlotly
        # chart-studio
        jupyterlab # Dev
        # flake8  # Dev
        # python-language-server
        # pyls-mypy
        toolz
        rdflib
        beautifulsoup4
        # requestsHtml
        networkx
        jsonpickle
        docker
        click
        pyvis
        pycurl
        # html2text
        pdftotext
        # wptools
        urlextract
        filelock
        pytest
        # docx2txt
        # flask
        nltk
        plotly
        # Etudier
        # selenium
        # etudier
        spacy
        spacy_models.en_core_web_lg
        langdetect
      ];
    };
in
  pkgs.mkShell {
    buildInputs = [ customPython anystyle-cli ]; #  chromedriver ];
  })
