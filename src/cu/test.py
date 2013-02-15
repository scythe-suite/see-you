from argparse import ArgumentParser
from os import symlink, unlink
from os.path import join, islink, isdir

from . import UPLOAD_DIR, all_uids, all_timestamps
from .testrunner import TestRunner, isots, rmrotree

def test( uid, timestamp = None, result_dir = None, clean = None ):
	if not result_dir: result_dir = UPLOAD_DIR
	if not timestamp: timestamp = max( all_timestamps( uid ) )
	dest_dir = join( result_dir, uid, timestamp )
	if isdir( dest_dir ):
		if clean: rmrotree( dest_dir )
		else: return 'skipped ({0} already exists, corresponding to time {1})'.format( dest_dir, isots( timestamp ) )
	with TestRunner( uid, timestamp ) as tr:
		tr.toxml()
		tr.saveto( dest_dir )
		tr_as_str = str( tr )
	latest = join( result_dir, uid, 'latest' )
	if islink( latest ): unlink( latest )
	symlink( timestamp, latest )
	return 'saved in {0} by {1}'.format( dest_dir, tr_as_str )

def main():

	parser = ArgumentParser( prog = 'cu test' )
	parser.add_argument( '--uid', help = 'The UID to test (default: all)' )
	parser.add_argument( '--result_dir', help = 'The destination directory where to copy the results directory (default: UPLOAD_DIR)' )
	parser.add_argument( '--timestamp', help = 'The timestamp of the upload to test (default: latest)' )
	parser.add_argument( '--clean', action='store_true', help = 'Whether to clean the destination result directory first' )
	args = parser.parse_args()

	for uid in [ args.uid ] if args.uid else all_uids():
		print 'Test for {0}: {1}'.format( uid, test( uid, args.timestamp, args.result_dir, args.clean ) )