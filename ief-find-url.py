# Written by @JamesHabben

import sqlite3
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Find a provided URL in an IEF SQLite database')
    parser.add_argument('-i', '--input', help='input IEF database file'),
    parser.add_argument('-o', '--output', help='output file for SQLite data')
    parser.add_argument('-s', '--search', help='optional search string')
    parser.add_argument('-l', '--limit', help='limit URL length (default=4000, 0=no limit)')
    args = parser.parse_args()

    try:
        conn = sqlite3.connect(args.input)
        cur = conn.cursor()
        conn2 = sqlite3.connect(args.output)
        cur2 = conn2.cursor()
        cur2.execute('create table if not exists urls (source, url)')
        cur2.execute('create index if not exists urlsidx on urls (source, url)')

        cur2.execute(
            # Unique URL list removing variation of http vs https
            'create view if not exists unique_urls as SELECT REPLACE (REPLACE (url, \'https://\', \'\'), \'http://\', \'\') AS url, '\
            'COUNT (url) AS urlcount FROM urls GROUP BY 1 ORDER BY 1')
        cur2.execute(
            # Unique list of domains with parts after slash (/) removed
            'create view if not exists unique_domains as '\
            'SELECT substr(url, 0, instr(url, \'/\')) AS url, sum(urlcount) as urlcount FROM unique_urls group by 1')
        cur2.execute(
            # Unique URL list further removing querystring data
            'create view if not exists unique_urls_no_qs as '\
            'select substr(url, 0, ifnull(nullif(instr(url, \'?\'),0),length(url)+1) ) as url, sum(urlcount) as urlcount from unique_urls group by 1')
        cur2.execute(
            # Unique URL list of image file extensions
            'create view if not exists filetype_images as select * from unique_urls_no_qs where url like \'%.gif\' or url like \'%.png\' '\
            'or url like \'%.jpg\' or url like \'%.jpeg\' or url like \'%.bmp\' or url like \'%.tif\'')
        cur2.execute(
            # Unique URL list of doc file extensions
            'create view if not exists filetype_docs as select * from unique_urls_no_qs where url like \'%.doc\' or url like \'%.docx\' '\
            'or url like \'%.xls\' or url like \'%.xlsx\' or url like \'%.ppt\' or url like \'%.pptx\' or url like \'%.pdf\' '\
            ' or url like \'%.rtf\' or url like \'%.pages\' or url like \'%.txt\'  or url like \'%.key\'')
        cur2.execute(
            # Unique URL list of executable extensions
            'create view if not exists filetype_executables as select * from unique_urls_no_qs where url like \'%.exe\' or url like \'%.dll\' ' \
            'or url like \'%.sys\' or url like \'%.bat\' or url like \'%.scr\' or url like \'%.jar\' or url like \'%.js\' '\
            ' or url like \'%.swf\' or url like \'%.pkg\' or url like \'%.app\' or url like \'%.deb\' or url like \'%.py\' '\
            ' or url like \'%.pl\' or url like \'%.ps1\' ')
        cur2.execute(
            # Unique URL list of archive extensions
            'create view if not exists filetype_archives as select * from unique_urls_no_qs where url like \'%.zip\' or url like \'%.7z\' ' \
            'or url like \'%.rar\' or url like \'%.cab\' or url like \'%.gz\' or url like \'%.tar\' or url like \'%.zipx\' ' \
            ' or url like \'%.iso\' or url like \'%.dmg\' ')

    except sqlite3.Error, error:
        print str(error)
        exit()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablist = cur.fetchall()

    for tabnam in tablist:
        #print tabnam
        cur.execute("pragma table_info('" + tabnam[0] + "')")
        collist = cur.fetchall()
        for val in collist:
            if val[1].find( 'URL') >= 0:
                print tabnam
                print val[1]

                if args.search:
                    cur.execute('select [{0}] from [{1}] where [{0}] like \'%{2}%\''.format(val[1], tabnam[0], args.search) )
                else:
                    cur.execute('select [{0}] from [{1}] '.format(val[1], tabnam[0]))

                for rec in cur:
                    #print 'insert into urls (source, url) values (\'{0}-{1}\', \'{2}\')'.format(val[1], tabnam[0], rec[0])
                    #print 'insert into urls (source, url) values (?, ?)', '{0}-{1}'.format(val[1], tabnam[0]), rec[0]
                    if args.limit == 0:
                        urlfield = rec[0]
                    elif args.limit:
                        urlfield = rec[0][0:args.limit]
                    elif rec[0] is not None:
                        urlfield = rec[0][0:4000]
                    cur2.execute('insert into urls (source, url) values (?, ?)', ('{0}-{1}'.format(val[1], tabnam[0]), urlfield))

                conn2.commit()


if __name__ == "__main__":
    main()
