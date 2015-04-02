__int64 GetFriendID( const char *pszAuthID )
{
	if(!pszAuthID)
		return 0;

	int iServer = 0;
	int iAuthID = 0;

	char szAuthID[64];
	strcpy_s(szAuthID, 63, pszAuthID);

	char *szTmp = strtok(szAuthID, ":");
	while(szTmp = strtok(NULL, ":"))
	{
		char *szTmp2 = strtok(NULL, ":");
		if(szTmp2)
		{
			iServer = atoi(szTmp);
			iAuthID = atoi(szTmp2);
		}
	}

	if(iAuthID == 0)
		return 0;

	__int64 i64friendID = (__int64)iAuthID * 2;

	//Friend ID's with even numbers are the 0 auth server.
	//Friend ID's with odd numbers are the 1 auth server.
	i64friendID += 76561197960265728 + iServer;

	return i64friendID;
}