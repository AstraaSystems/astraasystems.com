package Canada;

import java.util.*;
import JavaAPI.*;

public class AstraaTicketGenerator
{
    public static String generateCheckoutTicket(String orderAmount)
    {
        String store_id = "store5";
        String api_token = "yesguy";
        String processing_country_code = "CA";

        java.util.Date createDate = new java.util.Date();
        String order_id = "ASTRAA-" + createDate.getTime();

        CheckoutPreauth checkoutRequest = new CheckoutPreauth();
        checkoutRequest.setOrderId(order_id);
        checkoutRequest.setAmount(orderAmount);
        checkoutRequest.setCheckoutId("chktSPVV793136");

        HttpsPostRequest mpgReq = new HttpsPostRequest();
        mpgReq.setProcCountryCode(processing_country_code);
        mpgReq.setTestMode(false); 
        mpgReq.setStoreId(store_id);
        mpgReq.setApiToken(api_token);
        mpgReq.setTransaction(checkoutRequest);

        try {
            mpgReq.send();
            Receipt receipt = mpgReq.getReceipt();

            if ("true".equalsIgnoreCase(receipt.getComplete())) {
                String ticket = receipt.getTicket();
                System.out.println("[Astraa Backend] Generated Ticket Token: " + ticket);
                return ticket;
            } else {
                System.out.println("[Astraa Backend] Registration Failed: " + receipt.getMessage());
                return null;
            }
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
