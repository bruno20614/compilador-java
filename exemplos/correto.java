public class CalculadoraSimples {

    public static void main(String[] args) {

        int contador = 10;

        float taxa = 3.14;

        char quebra = '\n';

        String mensagem =
            "Analisador funcionando\n";

        contador += 2;

        if (
            contador >= 10
            && taxa != 0.0
        ) {

            System.out.println(
                mensagem
            );
        }

        // Comentário ignorado

        contador = contador - 1;

        /*
         * Comentário de bloco.
         */

        return;
    }
}