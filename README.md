# Initial setup
Before you launch PASSPY for the first time, you have to define the path to your 1Password.agilekeychain and the vault that you want to use in the file pass.cfg.

For fedora and probably other distributions there is an install.sh which creates an alias for your terminal and a .desktop file. This enables you to launch PASSPY like any other GNOME application but efore you can do so, you have to restart the GNOME shell (press Alt+F2 and enter "r").

# Usage
After you have launched PASSPY, you have to provide your password at the login screen:
![login](/resources/screenshots/login.png)

After you have logged in, the search field is focused and you can start searching immediately. When you hit "enter", the first item of the filtered list is selected. You can further navigate by using the arrow keys.
![search](/resources/screenshots/search.png)

You can filter the list of items by selecting one of the categories:
![search](/resources/screenshots/categories.png)

Whenever you select an entry in the rightmost column the corresponding value is copied to your clipboard.

# Remarks

PASSPY reads keychains created by 1Password by AgileBits. Aside from the fact that I'm using 1Password on other platforms I'm not affiliated with AgileBits.

# Acknowledgements

The keychain handling is based on the work of George Brock: [https://github.com/georgebrock/1pass](https://github.com/georgebrock/1pass)

