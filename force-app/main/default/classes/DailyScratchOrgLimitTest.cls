@isTest
public class DailyScratchOrgLimitTest {
    @isTest
    public static void testDailyScratchOrgLimit() {
        Integer orgLimit = Limits.getDailyScratchOrgs();
        Integer expectedLimit = 10; // Change this value to the expected limit
        
        System.assertEquals(expectedLimit, orgLimit, 'Incorrect daily scratch org limit');
    }
}
