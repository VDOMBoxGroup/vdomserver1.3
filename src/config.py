VDOM_CONFIG = {
	"SERVER-ID"                             : "5ED67D80-9017-4753-9633-685A1926A6B9",
	"DEFAULT-LANGUAGE"			: "en",
	"HTTP-ERROR-PAGES-DIRECTORY"		: "../errors",

	# managers directories
	"FILE-ACCESS-DIRECTORY"			: "../app",
	"XML-MANAGER-DIRECTORY"			: "../app",
	"APPLICATION-XML-TEMPLATE"		: "../app/app_template.xml",
	"SOURCE-MODULES-DIRECTORY"		: "../app/objects",

	# server stuff
	"SERVER-ADDRESS"			: "",
	"SERVER-PORT"				: 80,
	"SERVER-LOCALHOST-PORT"			: 2222,
	"VDOM-MEMORY-SERVER-PORT"		: 3333,
	"LOCALHOST-CARD-PORT"			: 4444,
	"LOCALHOST-LOGGER-PORT"			: 5555,
	"SERVER-PIDFILE"			: "../app/server.pid",
	"LOGGER-PIDFILE"			: "../app/logger.pid",
	"SERVER-SOURCE-MANAGER-MEMORY-QUOTE"	: "10240",
	"AUTO-REMOVE-INCORRECT-APPLICATIONS"	: 0,

	# special URLs
	"SOAP-POST-URL"				: "/SOAP",
	"MANAGEMENT-URL"			: "/system",
	"WSDL-FILE-URL"				: "/vdom.wsdl",
	"WSDL-FILE-LOCATION"			: "../app/vdom.wsdl",

	"SOURCE-TYPES-LOCATION"			: "../types",
	"TYPES-LOCATION"			: "../app/types",

	# log
	"LOG-FILE-SIZE"				: 500000,		# size of one log file
	"LOG-FILE-COUNT"			: 10,			# max number of log files to store (history)

	# session stuff
	"SESSION-LIFETIME"			: 1200,

	# timeouts
	"COMPUTE-TIMEOUT"			: 30.1,
	"RENDER-TIMEOUT"			: 30.1,
	"WYSIWYG-TIMEOUT"			: 30.1,
	"APP-SAVE-TIMEOUT"			: 30.1,

	"STORAGE-DIRECTORY"			: "../app",
	"TEMP-DIRECTORY"			: "../app/temp",	# must be without spaces!
	"FONT-DIRECTORY"			: "../fonts",
	"BACKUP-DIRECTORY"			: "../app/backup",
	"SHARE-DIRECTORY"			: "../app/share",
        "FILE-STORAGE-DIRECTORY"                : "../app/storage",
	"LIB-DIRECTORY"				: "../app/lib",
	"LOG-DIRECTORY"				: "../app/log",

	# storage keys
	"XML-MANAGER-TYPE-STORAGE-RECORD"	: "XML_TYPE_DATA",
	"XML-MANAGER-APP-STORAGE-RECORD"	: "XML_APPLICATION_DATA",
	"VIRTUAL-HOSTING-STORAGE-RECORD"	: "VIRTUAL_HOSTING_DATA",
        "FILE-MANAGER-INDEX-STORAGE-RECORD"     : "STORAGE_FILE_INDEX",
	"RESOURCE-MANAGER-INDEX-STORAGE-RECORD"	: "RESOURCE_FILE_INDEX",
	"DATABASE-MANAGER-INDEX-STORAGE-RECORD"	: "DATABASE_FILE_INDEX",
        "SCHEDULER-MANAGER-INDEX-STORAGE-RECORD": "SCHEDULER_INDEX",
	"BACKUP-STORAGE-DRIVER-INDEX-RECORD"    : "STORAGE_DRIVER_INDEX",
	"SOURCE-SWAP-FILE-INDEX-STORAGE-RECORD" : "SWAP_FILE_INDEX",
	"USER-MANAGER-STORAGE-RECORD" 		: "USER_INFO_DATA",
	"USER-MANAGER-ROOT-ID-STORAGE-RECORD" 	: "ROOT_USER_ID",
	"USER-MANAGER-GUEST-ID-STORAGE-RECORD" 	: "GUEST_USER_ID",
	"ACL-MANAGER-STORAGE-RECORD" 		: "ACL_ARRAY_DATA",
	"BACKUP-STORAGE-RECORD" 		: "BACKUP_CONFIG_DATA",
	"VDOM-CONFIG-1-RECORD" 			: "CONFIG_1_DATA",

	# vscript
	"DISABLE-VSCRIPT": 0
}

VDOM_CONFIG_1 = {
	"DEBUG"	:		"1",
	"DEBUG-ENABLE-TAGS" :	"0",
	"ENABLE-PAGE-DEBUG" :	"0",

	# email settings
	"SMTP-SENDMAIL-TIMEOUT"			: 20.0,
	"SMTP-SERVER-ADDRESS"			: "",
	"SMTP-SERVER-PORT"			: 25,
	"SMTP-SERVER-USER"			: "",
	"SMTP-SERVER-PASSWORD"			: "",

	# security
	"ROOT-PASSWORD"				: "root"
}
