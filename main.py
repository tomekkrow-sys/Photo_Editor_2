# main.py

from updater import check_for_updates, download_update, install_update

def main():
    has_update, new_version = check_for_updates()
    if has_update:
        print(f"New version available: {new_version}")
        if download_update(new_version):
            install_update(new_version)
    else:
        print("No updates available.")

if __name__ == "__main__":
    main()