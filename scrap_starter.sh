for i in 0 1 2
do
    echo "./batches/categs-$i.json" | python3 scrapping.py
done