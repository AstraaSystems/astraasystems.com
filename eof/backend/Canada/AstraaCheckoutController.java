package Canada;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import com.google.gson.Gson; // Or use your preferred JSON library
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/api/checkout/initiate")
public class AstraaCheckoutController extends HttpServlet 
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

        try {
            // 1. Securely set the standard package amount (e.g., $29.00) on the server side
            String paymentAmount = "29.00"; 

            System.out.println("[Astraa Controller] Requesting ticket from Moneris for amount: $" + paymentAmount);
            
            // 2. Fire the underlying ticket generation routine we created
            String ticket = AstraaTicketGenerator.generateCheckoutTicket(paymentAmount);

            if (ticket != null && !ticket.trim().isEmpty()) {
                jsonResponse.put("success", "true");
                jsonResponse.put("ticket", ticket);
                System.out.println("[Astraa Controller] Ticket successfully assigned to session client.");
            } else {
                jsonResponse.put("success", "false");
                jsonResponse.put("error", "Moneris gateway rejected transaction setup initialization.");
            }
        } catch (Exception e) {
            jsonResponse.put("success", "false");
            jsonResponse.put("error", "Internal server transaction crash: " + e.getMessage());
            e.printStackTrace();
        }

        out.print(gson.toJson(jsonResponse));
        out.flush();
    }
}
