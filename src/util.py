def print_records(records):
	if records.count()==0: print 'No records found!'

	for rec in records:
		print rec

def get_greater_than(fields,values):
	query = '{'

	assert len(fields)==len(values)

	for i in range(len(fields)):
		query+=fields[i]+':{"gt":'+str(values[i])+'},'
	return query+'}'