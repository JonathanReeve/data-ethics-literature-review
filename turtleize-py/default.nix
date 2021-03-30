with import <nixpkgs> {};

( let
    newPlotly = pkgs.python3Packages.buildPythonPackage rec {
      pname = "plotly";
      version = "4.6.0";

      src = pkgs.python3Packages.fetchPypi{
        inherit version; inherit pname;
        sha256 = "0br996lqbyq1prq9hhrzkgpicz5fgvxamzjrrpms20a2y1alkwv1";
      };

      buildInputs = with pkgs.python3Packages; [ decorator nbformat
                                                 pytz requests retrying six];
      doCheck = false;

    };

    newAltair = pkgs.python3Packages.buildPythonPackage rec {
      pname = "altair";
      version = "4.1.0";

      src = pkgs.python3Packages.fetchPypi{
        inherit version; inherit pname;
        sha256 = "0c99q5dy6f275yg1f137ird08wmwc1z8wmvjickkf2mvyka31p9y";
      };

      buildInputs = with pkgs.python3Packages; [
        entrypoints
        jinja2
        jsonschema
        numpy
        toolz
        pandas
        dominate # HTML DSL
      ];
      doCheck = false;

    };
    requestsHtml = pkgs.python38Packages.buildPythonPackage rec { 
	    pname = "requests-html"; 
	    version = "0.10.0";
	    src = pkgs.python38Packages.fetchPypi { 
	      inherit version; inherit pname; 
	      sha256 = "fpKez+2V+x0JlLs2gpXW18TQawP8uQDDPX0LF+YAOUc=";
	    };
	    propagatedBuildInputs = with pkgs.python38Packages; [ 
	      pyquery
	      requests
	      fake-useragent
	      parse
	      beautifulsoup4
	      pyppeteer
	      networkx
	      w3lib
	    ];
	    postPatch = ''
	      substituteInPlace setup.py --replace "bs4" "beautifulsoup4"
	    '';
	    doCheck = false;
    };
    etudier = pkgs.python38Packages.buildPythonPackage rec { 
	    pname = "etudier"; 
	    version = "0.0.7";
	    src = pkgs.python38Packages.fetchPypi { 
	      inherit version; inherit pname; 
	      sha256 = "0qy0h0bdlp1klzd3jjdky8l3z160cck0nlh5i3kgxgq1blsfkwb4";
	    };
	    buildInputs = with pkgs.python38Packages; [ 
	      selenium
	      networkx
	      requestsHtml
	    ];
	    nativeBuildInputs = [ chromedriver ];
	    doCheck = false;
    }; 
    customPython = pkgs.python38.buildEnv.override rec {
	    extraLibs = with pkgs.python38Packages; [
	      pkgs.chromedriver
	      matplotlib
	      pandas
	      jupyter
	      scikitlearn
	      newAltair
	      dominate
	      # plotly
	      newPlotly
	      # chart-studio
	      jupyterlab # Dev
	      # flake8  # Dev
	      # python-language-server
	      # pyls-mypy
	      toolz
	      rdflib
	      beautifulsoup4
	      requestsHtml
	      selenium
	      etudier
	      networkx
        docker
        click
	    ];
    };
    in 
    pkgs.mkShell { 
      buildInputs = [ customPython chromedriver ];
    })
