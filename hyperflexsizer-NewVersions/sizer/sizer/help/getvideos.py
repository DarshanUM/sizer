import wget
from sys import argv


def main():

    try:
        if argv[1] == "stage":
            url = 'https://cisco.box.com/shared/static/makyld0wcd69ttqtcfzmr03jpdfupzm5.gz'
            wget.download(url, 'videos.tar.gz')
        elif argv[1] == "production":
            url = 'https://cisco.box.com/shared/static/makyld0wcd69ttqtcfzmr03jpdfupzm5.gz'
            wget.download(url, 'videos.tar.gz')
        else:
            print("Usage: python getvideos.py <stage or production>")

    except Exception:

        print("Failed to get data from Cisco box link")
        raise


if __name__ == "__main__":
    main()
