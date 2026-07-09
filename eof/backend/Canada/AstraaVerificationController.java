package Canada;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import com.google.gson.Gson;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import JavaAPI.*;

@WebServlet("/api/checkout/verify")
public class AstraaVerificationController extends HttpServlet 
{
    private static final long serialVersionUID = 1L;

    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException 
    {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        PrintWriter out = response.getWriter();
        Gson gson = new Gson();
        HashMap<String, String> jsonResponse = new HashMap<>();

        // Get the ticket from the frontend payload
        HashMap<String, String> requestData = gson.fromJson(request.getReader(), HashMap.class);
        String clientTicket = requestData != null ? requestData.get("ticket") : null;

        if (clientTicket == null || clientTicket.trim().isEmpty()) {
            jsonResponse.put("success", "false");
            jsonResponse.put("error", "Missing or invalid ticket identifier parameter.");
            out.print(gson.toJson(jsonResponse));
            return;
        }

        try {
            String store_id = "store5";
            String api_token = "yesguy";
            String processing_country_code = "CA";

            System.out.println("[Astraa Verification] Querying Moneris for transaction state of ticket: " + clientTicket);

            // 1. Set up a status check verification transaction payload
            // Note: Verify the class name used for post-checkout verification checks in your exact Java SDK JAR
            CheckoutStatusCheck statusCheck = new CheckoutStatusCheck();
            statusCheck.setTicket(clientTicket);

            HttpsPostRequest mpgReq = new HttpsPostRequest();
            mpgReq.setProcCountryCode(processing_country_code);
            mpgReq.setTestMode(false);
            mpgReq.setStoreId(store_id);
            mpgReq.setApiToken(api_token);
            mpgReq.setTransaction(statusCheck);

            // 2. Transmit the status check query request
            mpgReq.send();
            Receipt receipt = mpgReq.getReceipt();

            // 3. Inspect if the payment was successfully captured
            if ("true".equalsIgnoreCase(receipt.getComplete()) && "001".equals(receipt.getResponseCode())) {
                jsonResponse.put("success", "true");
                jsonResponse.put("amount", receipt.getTransAmount());
                jsonResponse.put("message", "Transaction verified successfully.");
                System.out.println("[Astraa Verification] Capture confirmed for amount: " + receipt.getTransAmount());
            } else {
                jsonResponse.put("success", "false");
                jsonResponse.put("error", "Transaction verification failed or remained uncaptured: " + receipt.getMessage());
            }
        } catch (Exception e) {
            jsonResponse.put("success", "false");
            jsonResponse.put("error", "Internal security system crash: " + e.getMessage());
            e.printStackTrace();
        }

        out.print(gson.toJson(jsonResponse));
        out.flush();
    }
}
