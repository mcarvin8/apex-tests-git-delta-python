@isTest
public class UserEmailValidationTest {
    @isTest
    public static void testInvalidEmail() {
        User testUser = new User(
            LastName = 'Doe',
            Email = 'invalid-email'
        );
        
        Test.startTest();
        try {
            insert testUser;
            System.assert(false, 'An invalid email should have thrown an exception.');
        } catch (DmlException e) {
            String expectedErrorMessage = 'Invalid email address: invalid-email';
            System.assertEquals(expectedErrorMessage, e.getDmlMessage(0));
        }
        Test.stopTest();
    }
}
