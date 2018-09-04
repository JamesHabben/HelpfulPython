import plistlib
import glob
import json
import argparse

argParser = argparse.ArgumentParser(description='Recursively search a folder for \'info.plist\' files, and parse \'CFBundleURLSchemes\' out')
argParser.add_argument('-f', '--folder', help='Root folder to scan for .app/info.plist files')
argParser.add_argument('-g', '--grouped', help='Output format in grouped instead of JSON', action='store_true')
args = argParser.parse_args()

if args.folder:

    listplist = glob.glob(args.folder + '**/*.app/contents/info.plist', recursive=True)

    data=[]

    for p in sorted(listplist):
        with open(p, 'rb') as fp:
            pl = plistlib.load(fp)
            if 'CFBundleURLTypes' in pl:
                #print(p)
                for s in pl['CFBundleURLTypes']:
                    if 'CFBundleURLName' in s:
                        #print('  {} [{}://]'.format(s['CFBundleURLName'], s['CFBundleURLSchemes'][0]))
                        data.append({'app':p,'name':s['CFBundleURLName'],'scheme':s['CFBundleURLSchemes'][0]})
                    else:
                        #print('  -unnamed- [{}://]'.format(s['CFBundleURLSchemes'][0]))
                        data.append({'app': p, 'name': '', 'scheme': s['CFBundleURLSchemes'][0]})

    if args.grouped:
        import pandas

        df = pandas.DataFrame(data)
        print(df.groupby('scheme').size().sort_values(ascending=False))
    else:
        print(json.dumps(data))

