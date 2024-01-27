# webcrawler

## Instructions to run 
1. Clone the repository
```
git clone https://github.com/AmanTahiliani/webcrawler.git
```
2. cd into the directory
```
cd webcrawler
```
3. Install the requirements
```
pip install -r requirements.txt
```
4. Run the shell script
```
./amantahiliani.sh 
```

Note: If you get a permission denied error, run the following command
```
chmod +x amantahiliani.sh
```
If it still doesn't work, run the following command
```
python3 MultiThreadedCrawler.py {seed_url} --pages_to_parse=1000
```


## Output
The output is generated in the form of the following files:
1. pages_per_second.png - A graph showing the number of pages crawled per second
2. craw_ratio_table.png-   A table showing the ratio of pages crawled to pages discovered
3. crawlspeed.png- A graph showing the crawl speed in pages per minute
4. Keywords_Output.json- A json file containing the keywords and the urls they were found in along with the frequency of the keyword in the url