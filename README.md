**BlueCipher - Encryption/Decryption**

[ **DESCRIPTION** ]: Book Cipher Automation Tool

Book ciphers are an old-school, slow and string style of encryption that maps each character in a message to three numbers - the page number, line number on that page, and character number on that line. BC uses the following format:

    [ FORMAT ]: <page>-<line>-<character>

    [ Ex ]: 10-7-23,11-12-8,...

[ **NOTE** ]: The <character> segment of the code can be anything at that coordinate in the keytext file, case sensitive and including whitespaces for a more accurate transimition.

BlueCipher automates the decryption of ciphertext or encryption of cleartext from both a CLI menu and using input/output files on the basis of a auto-generated keytext file created by concatonating chapter files in a order dictated by the keycode.

As with everything there are tradeoffs, but the design decessions make it -

* Light weight and highly portable as a single python file;

* OS agnostic - packaged in such a way that it can be run like a standalone script on Windows machines as well as an installable consumable package for pip (that can be build locally using the Build WizZard script) on Linux;

* Simple to use and to understand, even for your tech savy grandma ;)

* Use keytext that can be randomly generated or actual segments of a known book (that the cryptographer doesn't even need to know how to read);

[ **BONUS** ]: Book ciphers can be also be used in that offline meatspace, although encryption and decryption would be at the speed of a Covert Tazmanian Snail - weather this should mean anything to you or not depends on what kind of games you've gotten yourself into;

[ **EXAMPLES** ]: Running as a standalone script

    [ Ex ]: Run in interactive mode using the terminal as a data source

        ~$ ./blue_cipher.py

    [ Ex ]: Run using the parameters specified in the config file

        ~$ ./blue_cipher.py --konfig-file conf/blue_cipher.conf/json

    [ Ex ]: Run decryption procedure using files on disk as a data source

        ~$ ./blue_cipher.py
            --action decrypt \
            --key-code 123456 \
            --ciphertext-file bc_cipher.txt \
            --keytext-dir text

    [ Ex ]: Run encryption procedure with no STDOUT using files as a data source

        ~$ ./blue_cipher.py
            --action encrypt \
            --key-code 123456 \
            --cleartext-file bc_clear.txt \
            --keytext-dir text \
            --silent

    [ Ex ]: Cleanup all created files with no STDOUT messages

        ~$ ./blue_cipher.py --action cleanup --silent

[ **EXAMPLES** ]: Building consumable artifact

    [ Ex ]: Cleanup build files with no manual interaction, install dependencies, ensure project file structure, build Python3 package and install it in a virtual environment using pip -

        ~$ ./build.sh --cleanup -y --setup BUILD INSTALL

    [ Ex ]: Run project autotesters -

        ~$ ./build.sh --test

[ **EXAMPLES** ]: Running as a system util (requires package build and install)

    [ Ex ]: Run in interactive mode using the terminal as a data source

        ~$ bluecipher

    [ Ex ]: Run using the parameters specified in the config file

        ~$ bluecipher --konfig-file conf/blue_cipher.conf.json

[ **Q/A** ]: Did YOU Know??

* Chapter files used in building the keytext file require a .txt extension, and are usually numbered in order to create a short keycode;

* The maximum length of the keycode is dictated by the number of chapter files available, and contains the names of the files in a certain order without the extension .txt;

* The keytext is cached in its entirety before encrypting or decrypting, which is not optimal when running in a file base mode, but helps when the data source is the CLI menu used when running the script without any arguments;


Excellent Regards,

